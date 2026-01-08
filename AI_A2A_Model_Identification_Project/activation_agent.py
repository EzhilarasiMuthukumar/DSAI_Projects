import json
import os
from typing import Dict, Any, List
from a2a_protocol import Agent, Message


class ActivationHelper(Agent):
    def __init__(self):
        super().__init__("ActivationHelper")
        self.version = "1.0.0"
        self.description = "Recommends activation functions for neural network layers"
        self.activations = self.load_activations()
    
    def load_activations(self) -> Dict[str, List[Dict[str, str]]]:
        json_path = os.path.join(os.path.dirname(__file__), 'data', 'activation_knowledge.json')
        with open(json_path, 'r') as f:
            return json.load(f)
    
    def get_capabilities(self) -> List[str]:
        return ["recommend_activation"]
    
    def get_capability_schemas(self) -> Dict[str, Dict[str, Any]]:
        return {
            'recommend_activation': {
                'input': {
                    'layer_type': 'string (hidden, output)',
                    'problem_type': 'string (classification, regression, etc.)',
                    'layer_position': 'string (first, middle, last)',
                    'network_depth': 'integer'
                },
                'output': {
                    'layer_type': 'string',
                    'problem_type': 'string',
                    'recommendations': 'list of {function, formula?, reasoning, use_when, note?}',
                    'agent': 'string'
                }
            }
        }
    
    def handle_request(self, message: Message) -> Message:
        if message.capability != "recommend_activation":
            return Message("response", message.capability, {
                "error": f"Unknown capability: {message.capability}"
            })
        
        layer_type = message.data.get("layer_type", "hidden")
        problem_type = message.data.get("problem_type", "classification")
        layer_position = message.data.get("layer_position", "middle")
        network_depth = message.data.get("network_depth", 3)
        
        recommendations = self.pick_activations(
            layer_type, problem_type, layer_position, network_depth
        )
        
        return Message("response", "recommend_activation", {
            "layer_type": layer_type,
            "problem_type": problem_type,
            "recommendations": recommendations,
            "agent": self.name
        })
    
    def pick_activations(self, layer_type: str, problem_type: str,
                          layer_position: str, network_depth: int) -> List[Dict[str, str]]:
        recommendations = []
        
        if layer_type == "hidden":
            for activation_info in self.activations["hidden_layer"]:
                rec = {
                    "function": activation_info["function"],
                    "formula": activation_info["formula"],
                    "reasoning": activation_info["reasoning"],
                    "use_when": activation_info["use_when"]
                }
                
                if activation_info["function"] == "ReLU":
                    rec["note"] = "Recommended as default choice for hidden layers"
                elif activation_info["function"] == "Leaky ReLU" and network_depth > 10:
                    rec["note"] = "Consider for very deep networks to prevent dying neurons"
                
                recommendations.append(rec)
        
        elif layer_type == "output":
            if "binary" in problem_type.lower() or "classification" in problem_type.lower():
                if "multiclass" in problem_type.lower() or "multi" in problem_type.lower():
                    key = "output_multiclass_classification"
                else:
                    key = "output_binary_classification"
            elif "regression" in problem_type.lower():
                key = "output_regression"
            else:
                key = "output_binary_classification"
            
            if key in self.activations:
                for activation_info in self.activations[key]:
                    rec = {
                        "function": activation_info["function"],
                        "formula": activation_info["formula"],
                        "reasoning": activation_info["reasoning"],
                        "use_when": activation_info["use_when"],
                        "note": "Standard choice for this problem type"
                    }
                    recommendations.append(rec)
        
        if not recommendations:
            recommendations.append({
                "function": "ReLU",
                "reasoning": "Default safe choice when unsure",
                "note": "Generally works well for most scenarios"
            })
        
        return recommendations
