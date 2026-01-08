#!/usr/bin/env python3

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from rdflib import Graph, Namespace

"""
Recipe Box MCP Server

A simple MCP server to retrieve recipe data from an RDF knowledge graph.
Used SPARQL to search recipes by cuisine, spice level, allergens, and analyze the chef's performance.
"""


# RDF graph where all the recipe data are kept
graph = Graph()

# The namespaces used in our ontology
EX = Namespace("http://example.org/food/schema#")
DATA = Namespace("http://example.org/food/data#")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")

# Binding these namespaces to use as shorthand in query
graph.bind("ex", EX)
graph.bind("d", DATA)
graph.bind("foaf", FOAF)


def load_rdf_data():
    try:
        rbox_file = Path(__file__).parent / "rbox.ttl"
        
        if not rbox_file.exists():
            raise FileNotFoundError(f"not finding rbox.ttl at {rbox_file}")
        
        graph.parse(rbox_file, format="turtle")
        print(f"Loaded {len(graph)} triples from rbox.ttl", file=sys.stderr, flush=True)
        
    except Exception as e:
        print(f"error : {e}", file=sys.stderr, flush=True)
        raise


def query_graph(sparql_query: str) -> list:
    try:
        results = graph.query(sparql_query)
        return list(results)
    except Exception as e:
        print(f"query error: {e}", file=sys.stderr, flush=True)
        return []


# Tool handlers

async def search_recipes_by_cuisine(cuisine: str) -> list[dict]:
    query = f"""
    PREFIX ex: <http://example.org/food/schema#>
    PREFIX d: <http://example.org/food/data#>
    
    SELECT ?recipe ?prepTime ?cookTime ?budget ?spicelevel
    WHERE {{
        ?recipe ex:hasCuisine d:{cuisine.lower()} .
        OPTIONAL {{ ?recipe ex:prepTime ?prepTime }}
        OPTIONAL {{ ?recipe ex:cookTime ?cookTime }}
        OPTIONAL {{ ?recipe ex:budget ?budget }}

        OPTIONAL {{ 
            ?recipe ex:hasSpiceLevel ?spiceLevelURI .
            BIND(REPLACE(STR(?spiceLevelURI), ".*#", "") AS ?spicelevel)
        }}
    }}
    """
    
    results = query_graph(query)
    recipes = []
    
    for row in results:
        recipe_name = str(row.recipe).split("#")[1]
        
        recipes.append({
            "name": recipe_name,
            "prepTime": str(row.prepTime) if row.prepTime else None,
            "cookTime": str(row.cookTime) if row.cookTime else None,
            "budget": str(row.budget) if row.budget else None,
            "spiceLevel": str(row.spiceLevel) if row.spiceLevel else None
        })
    
    return recipes


async def search_by_spice_level(spice_level: str) -> list[dict]:
    query = f"""
    PREFIX ex: <http://example.org/food/schema#>
    PREFIX d: <http://example.org/food/data#>
    
    SELECT ?recipe ?cuisine ?bgt
    WHERE {{
        ?recipe ex:hasSpiceLevel d:{spice_level.lower()} .
        OPTIONAL {{ 
            ?recipe ex:hasCuisine ?cuisineURI .
            BIND(REPLACE(STR(?cuisineURI), ".*#", "") AS ?cuisine)
        }}

        OPTIONAL {{ ?recipe ex:budget ?bgt }}
    }}
    """
    
    results = query_graph(query)
    recipes = []
    
    for row in results:
        recipe_name = str(row.recipe).split("#")[1]
        
        recipes.append({
            "name": recipe_name,
            "cuisine": str(row.cuisine) if row.cuisine else None,
            "budget": str(row.bgt) if row.bgt else None,
            "spiceLevel": spice_level
        })
    
    return recipes


async def check_allergens(allergen: str) -> list[dict]:

    query = f"""
    PREFIX ex: <http://example.org/food/schema#>
    PREFIX d: <http://example.org/food/data#>
    
    SELECT DISTINCT ?recipe ?ingredient
    WHERE {{
        {{
            ?recipe ex:allergen d:{allergen} .
        }} UNION {{
            ?recipe ex:hasIngredient ?ingredientURI .
            ?ingredientURI ex:allergen d:{allergen} .
            BIND(REPLACE(STR(?ingredientURI), ".*#", "") AS ?ingredient)
        }}
    }}
    """
    
    results = query_graph(query)
    recipes = []
    seen = set()
    
    for row in results:
        recipe_name = str(row.recipe).split("#")[1]
        
        if recipe_name not in seen:
            seen.add(recipe_name)
            
            recipes.append({
                "name": recipe_name,
                "allergen": allergen,
                "ingredient": str(row.ingredient) if row.ingredient else "recipe-level"
            })
    
    return recipes


async def get_chef_performance(chef_name: str) -> dict:
    query = f"""
    PREFIX ex: <http://example.org/food/schema#>
    PREFIX d: <http://example.org/food/data#>
    
    SELECT ?recipe ?rating ?chefname ?email
    WHERE {{
        ?recipe ex:preparedBy d:{chef_name} .
        d:{chef_name} ex:chefName ?chefname .
        OPTIONAL {{ d:{chef_name} ex:contactEmail ?email }}
        OPTIONAL {{
            ?review ex:forRecipe ?recipe .
            ?review ex:rating ?rating .
        }}
    }}
    """
    
    results = query_graph(query)
    recipes = []
    ratings = []
    chef_info = {}
    
    for row in results:
        recipe_name = str(row.recipe).split("#")[1]
        
        if recipe_name not in recipes:
            recipes.append(recipe_name)
        
        if row.rating:
            ratings.append(float(row.rating))
        
        if not chef_info:
            chef_info = {
                "name": str(row.chefname),
                "email": str(row.email) if row.email else None
            }
    
    avg_rating = sum(ratings) / len(ratings) if ratings else 0
    
    return {
        "chef": chef_info,
        "recipes_prepared": recipes,
        "total_recipes": len(recipes),
        "total_reviews": len(ratings),
        "average_rating": round(avg_rating, 2)
    }


# Creating the MCP server
app = Server("recipe-box-mcp-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_recipes_by_cuisine",
            description="Search for recipes by cuisine type (italian, chinese,  indian)",
            inputSchema={
                "type": "object",
                "properties": {
                    "cuisine": {
                        "type":  "string",
                        "description": "Cuisine type (e.g., italian, chinese, indian)"
                    }
                },
                "required": ["cuisine"]
            }
        ),
        Tool(
            name="search_by_spice_level",
            description="Find recipes by spice level (mild, medium, hot)",
            inputSchema={
                "type": "object",
                "properties": {
                    "spice_level": {
                        "type": "string",
                        "description":  "Spice level: mild, medium, or hot"
                    }
                },
                "required":  ["spice_level" ]
            }
        ),
        Tool(
            name="check_allergens",
            description="Check if recipes contain specific allergens (Dairy, Gluten)",
            inputSchema={
                "type":  "object",
                "properties": {
                    "allergen": {
                        "type": "string",
                        "description":  "Allergen type (e.g., Dairy, Gluten)"
                    }
                },
                "required": ["allergen"]
            }
        ),
        Tool(
            name="get_chef_performance",
            description="Get chef statistics including recipes prepared and average ratings",
            inputSchema={
                "type": "object",
                "properties": {
                    "chef_name": {
                        "type":  "string",
                        "description": "Chef identifier (e.g., chef_david, chef_maria, chef_priya)"
                    }
                },
                "required": [ "chef_name"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    
    if name == "search_recipes_by_cuisine":
        results = await search_recipes_by_cuisine(arguments["cuisine"])
        return [TextContent(type="text", text=json.dumps(results, indent=2))]
    
    elif name == "search_by_spice_level":
        results = await search_by_spice_level(arguments["spice_level"])
        return [TextContent(type="text", text=json.dumps(results, indent=2))]
    
    elif name == "check_allergens":
        results = await check_allergens(arguments["allergen"])
        return [TextContent(type="text", text=json.dumps(results, indent=2))]
    
    elif name == "get_chef_performance":
        results = await get_chef_performance(arguments["chef_name"])
        return [TextContent(type="text", text=json.dumps(results, indent=2))]
    
    else:
        raise ValueError(f"not a known tool: {name}")


async def main():

    load_rdf_data()
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream, 
            write_stream, 
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
