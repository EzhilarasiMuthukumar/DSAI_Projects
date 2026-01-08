import json
import os


def load_problems():
    json_path = os.path.join(os.path.dirname(__file__), 'data', 'use_cases.json')
    with open(json_path, 'r') as f:
        return json.load(f)


problems = load_problems()


def get_problem(problem_id: int):
    for case in problems:
        if case['id'] == problem_id:
            return case
    return None


def get_all_problems():
    return problems
