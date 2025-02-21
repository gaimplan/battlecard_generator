import json
import os
from typing import Dict, Any

def load_json_file(file_path: str) -> Dict[Any, Any]:
    """Load a JSON file and return its contents."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: File {file_path} not found. Skipping...")
        return {}
    except json.JSONDecodeError:
        print(f"Warning: File {file_path} contains invalid JSON. Skipping...")
        return {}

def combine_json_files():
    # Define the files in the desired order with paths in temp_files directory
    temp_dir = "temp_files"
    files = [
        os.path.join(temp_dir, 'strategic_overview.json'),
        os.path.join(temp_dir, 'value_propositions.json'),
        os.path.join(temp_dir, 'qualifying.json'),
        os.path.join(temp_dir, 'usecases.json'),
        os.path.join(temp_dir, 'competitive.json'),
        os.path.join(temp_dir, 'objection_handling.json'),
        os.path.join(temp_dir, 'action_plan.json'),
    ]

    # Create the combined structure
    combined_data = {
        "battlecard": {
            "strategic_overview": {},
            "value_propositions": {},
            "qualifying_questions": {},
            "use_cases": {},
            "competitive_analysis": {},
            "objection_handling": {},
            "action_plan": {}
        }
    }

    # Map file names to their corresponding keys in the combined structure
    file_to_key = {
        'strategic_overview.json': 'strategic_overview',
        'value_propositions.json': 'value_propositions',
        'qualifying.json': 'qualifying_questions',
        'usecases.json': 'use_cases',
        'competitive.json': 'competitive_analysis',
        'objection_handling.json': 'objection_handling',
        'action_plan.json': 'action_plan'
    }

    # Load and combine each file
    for file_path in files:
        data = load_json_file(file_path)
        if data:
            key = file_to_key[os.path.basename(file_path)]
            combined_data["battlecard"][key] = data

    # Write the combined data to the output directory
    output_file = os.path.join("output", 'battlecard.json')
    with open(output_file, 'w') as f:
        json.dump(combined_data, f, indent=4)
    
    print(f"Successfully combined all JSON files into {output_file}")

if __name__ == "__main__":
    combine_json_files()
