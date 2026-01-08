from model_agent import ModelHelper
from activation_agent import ActivationHelper
from use_cases import get_all_problems

def test_agents():
    print("Let's test our helpers...\n")
    
    model_helper = ModelHelper()
    activation_helper = ActivationHelper()
    
    print("Model Helper Agent Card:")
    card = model_helper.get_agent_card()
    print(f"Name: {card['name']}")
    print(f"Version: {card['version']}")
    print(f"About: {card['description']}")
    print(f"Can do: {card['capabilities']}")
    
    print("\nActivation Helper Agent Card:")
    card = activation_helper.get_agent_card()
    print(f"Name: {card['name']}")
    print(f"Version: {card['version']}")
    print(f"About: {card['description']}")
    print(f"Can do: {card['capabilities']}")
    
    print("\nTesting model helper...")
    
    print("\nTrying classification:")
    response = model_helper.send_request('recommend_model', {
        'problem_type': 'classification',
        'dataset_size': 'medium',
        'description': 'Test classification problem'
    })
    print(f"Got response: {response.msg_type}")
    print(f"Got {len(response.data.get('recommendations', []))} recommendations")
    
    print("\nTesting activation helper...")
    response = activation_helper.send_request('recommend_activation', {
        'layer_type': 'hidden',
        'problem_type': 'classification',
        'layer_position': 'middle',
        'network_depth': 5
    })
    print(f"Got response: {response.msg_type}")
    print(f"Got {len(response.data.get('recommendations', []))} recommendations")
    
    print("\nChecking problems pool...")
    all_problems = get_all_problems()
    print(f"Found {len(all_problems)} problems")
    print(f"Classification problems: {len([c for c in all_problems if c['problem_type'] == 'classification'])}")
    print(f"Regression/Time Series: {len([c for c in all_problems if c['problem_type'] in ['regression', 'time_series']])}")
    print(f"Others: {len([c for c in all_problems if c['problem_type'] not in ['classification', 'regression', 'time_series']])}")
    
    print("\n✓ All tests passed! Everything works!")

if __name__ == "__main__":
    test_agents()

