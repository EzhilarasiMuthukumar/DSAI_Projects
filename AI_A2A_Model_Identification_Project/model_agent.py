import json
import os
from typing import Dict, Any, List
from a2a_protocol import Agent, Message


class ModelHelper(Agent):
    def __init__(self):
        super().__init__("ModelHelper")
        self.version = "1.0.0"
        self.description = "Recommends ML models based on problem type and characteristics"
        self.models = self.load_models()
    
    def load_models(self) -> Dict[str, List[Dict[str, str]]]:
        json_path = os.path.join(os.path.dirname(__file__), 'data', 'model_knowledge.json')
        with open(json_path, 'r') as f:
            return json.load(f)
    
    def get_capabilities(self) -> List[str]:
        return ['recommend_model']
    
    def get_capability_schemas(self) -> Dict[str, Dict[str, Any]]:
        return {
            'recommend_model': {
                'input': {
                    'problem_type': 'string (classification, regression, clustering, time_series, dimensionality_reduction)',
                    'dataset_size': 'string (small, medium, large)',
                    'description': 'string',
                    'num_features': 'integer'
                },
                'output': {
                    'problem_type': 'string',
                    'recommendations': 'list of {model, reasoning, use_when, note?}',
                    'agent': 'string'
                }
            }
        }
    
    def handle_request(self, message: Message) -> Message:
        if message.capability != 'recommend_model':
            return Message('response', message.capability, {
                'error': f'Unknown capability: {message.capability}'
            })
        
        problem_type = message.data.get('problem_type', '').lower()
        dataset_size = message.data.get('dataset_size', 'medium')
        description = message.data.get('description', '')
        
        recommendations = self.pick_models(problem_type, dataset_size, description)
        
        return Message('response', 'recommend_model', {
            'problem_type': problem_type,
            'recommendations': recommendations,
            'agent': self.name
        })
    
    def pick_models(self, problem_type: str, dataset_size: str, 
                     description: str) -> List[Dict[str, str]]:
        if problem_type not in self.models:
            return [{
                'model': 'Unknown Problem Type',
                'reasoning': f'No recommendations available for problem type: {problem_type}'
            }]
        
        available_models = self.models[problem_type]
        recommendations = []
        
        for i, model_info in enumerate(available_models[:3]):
            rec = {
                'model': model_info['model'],
                'reasoning': model_info['reasoning'],
                'use_when': model_info['use_when']
            }
            
            if dataset_size == 'small' and i == 0:
                rec['note'] = 'Good starting point for small datasets'
            elif dataset_size == 'large' and 'scalable' in model_info['reasoning'].lower():
                rec['note'] = 'Particularly suitable for large datasets'
            
            recommendations.append(rec)
        
        return recommendations
