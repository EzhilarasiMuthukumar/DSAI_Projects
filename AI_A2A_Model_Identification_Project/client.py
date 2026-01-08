#!/usr/bin/env python3

import random
from typing import List, Dict, Any
from model_agent import ModelHelper
from activation_agent import ActivationHelper
from use_cases import get_all_problems
from a2a_protocol import AgentRegistry


class RecommendationApp:
    def __init__(self):
        ModelHelper()
        ActivationHelper()
        
        self.all_problems = get_all_problems()
        
        print("Discovering available helpers...")
        agents = AgentRegistry.list_all()
        for agent in agents:
            print(f"Found: {agent.name} - {agent.description}")
    
    def pick_random_problems(self, count: int = 5) -> List[Dict[str, Any]]:
        return random.sample(self.all_problems, min(count, len(self.all_problems)))
    
    def show_problems(self, problems: List[Dict[str, Any]]):
        print("\nPick a problem to solve:")
        print("\nWhich one interests you?\n")
        
        for i, case in enumerate(problems, 1):
            print(f"{i}. {case['name']}")
            print(f"   Type: {case['problem_type'].title()}")
            print(f"   {case['description']}")
            print()
    
    def get_user_choice(self, max_options: int) -> int:
        while True:
            try:
                choice = input(f"Enter your choice (1-{max_options}): ").strip()
                choice_num = int(choice)
                
                if 1 <= choice_num <= max_options:
                    return choice_num - 1
                else:
                    print(f"Please enter a number between 1 and {max_options}")
            except ValueError:
                print("Please enter a valid number")
            except KeyboardInterrupt:
                print("\n\nExiting...")
                exit(0)
    
    def ask_model_helper(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        agents = AgentRegistry.discover('recommend_model')
        if not agents:
            return {'error': 'No model recommendation agent found'}
        
        helper = agents[0]
        info = {
            'problem_type': problem['problem_type'],
            'dataset_size': problem['dataset_size'],
            'description': problem['description'],
            'num_features': problem['num_features']
        }
        
        response = helper.send_request('recommend_model', info)
        return response.data
    
    def ask_activation_helper(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        if not problem.get('use_neural_network', False):
            return None
        
        agents = AgentRegistry.discover('recommend_activation')
        if not agents:
            return None
        
        helper = agents[0]
        hidden_info = {
            'layer_type': 'hidden',
            'problem_type': problem['sub_type'],
            'layer_position': 'middle',
            'network_depth': 5
        }
        
        output_info = {
            'layer_type': 'output',
            'problem_type': problem['sub_type'],
            'layer_position': 'last',
            'network_depth': 5
        }
        
        hidden_response = helper.send_request('recommend_activation', hidden_info)
        output_response = helper.send_request('recommend_activation', output_info)
        
        return {
            'hidden_layer': hidden_response.data,
            'output_layer': output_response.data
        }
    
    def show_recommendations(self, problem: Dict[str, Any], 
                            model_recs: Dict[str, Any],
                            activation_recs: Dict[str, Any] = None):
        print("\nHere's what I found:")
        
        print(f"\nYour problem: {problem['name']}")
        print(f"Type: {problem['problem_type'].title()}")
        print(f"About: {problem['description']}")
        print(f"Dataset size: {problem['dataset_size'].title()}")
        print(f"Features: {problem['num_features']}")
        
        print("\nModel suggestions:")
        
        if 'recommendations' in model_recs:
            for i, rec in enumerate(model_recs['recommendations'], 1):
                print(f"\n{i}. {rec['model']}")
                print(f"   Reasoning: {rec['reasoning']}")
                print(f"   Best for: {rec['use_when']}")
                if 'note' in rec:
                    print(f"   Tip: {rec['note']}")
        
        if activation_recs:
            print("\nActivation functions (for neural networks):")
            
            print("\nFor hidden layers:")
            if 'recommendations' in activation_recs['hidden_layer']:
                for i, rec in enumerate(activation_recs['hidden_layer']['recommendations'], 1):
                    print(f"\n{i}. {rec['function']}")
                    if 'formula' in rec:
                        print(f"   Formula: {rec['formula']}")
                    print(f"   Why: {rec['reasoning']}")
                    if 'note' in rec:
                        print(f"   Tip: {rec['note']}")
            
            print("\nFor output layer:")
            if 'recommendations' in activation_recs['output_layer']:
                for i, rec in enumerate(activation_recs['output_layer']['recommendations'], 1):
                    print(f"\n{i}. {rec['function']}")
                    if 'formula' in rec:
                        print(f"   Formula: {rec['formula']}")
                    print(f"   Why: {rec['reasoning']}")
                    if 'note' in rec:
                        print(f"   Tip: {rec['note']}")
    
    def run(self):
        print("\nWelcome! Let's find the right ML approach for you.")
        print("Using our helper agents to recommend models...")
        
        problems = self.pick_random_problems(5)
        self.show_problems(problems)
        
        choice_idx = self.get_user_choice(len(problems))
        picked_problem = problems[choice_idx]
        
        print(f"\nNice choice: {picked_problem['name']}")
        print("Let me ask the helpers...\n")
        
        model_recs = self.ask_model_helper(picked_problem)
        activation_recs = self.ask_activation_helper(picked_problem)
        
        self.show_recommendations(
            picked_problem,
            model_recs,
            activation_recs
        )
        
        print("\nWant to try another? (y/n): ", end="")
        response = input().strip().lower()
        
        if response == 'y':
            self.run()
        else:
            print("\nThanks for using this! Hope it helped!\n")


def main():
    app = RecommendationApp()
    app.run()


if __name__ == "__main__":
    main()
