import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from langchain_community.document_loaders import JSONLoader
from dotenv import load_dotenv
import json
import re
from run import PRODUCT_NAME
from langchain_google_genai import GoogleGenerativeAI

# Load environment variables from .env file for API keys
load_dotenv()

model_local = GoogleGenerativeAI(model="gemini-2.0-flash", verbose=True, temperature=0.2, google_api_key=os.environ.get("GOOGLE_API_KEY"))

def gpt_prompt(prompt):
    try:
        response = model_local.invoke(prompt)
        if response:
            return response.strip()
        return ""
    except Exception as e:
        print(f"Error occurred: {e}")
        return ""

print("Welcome!")

# Ensure directories exist
os.makedirs('logs', exist_ok=True)
os.makedirs('temp_files', exist_ok=True)
os.makedirs('output', exist_ok=True)

try:
    # Load data from benefits_chunks.json
    with open('temp_files/benefits_chunks.json', 'r') as f:
        chunks = json.load(f)
    
    # Format chunks data
    formatted_content = []
    sources = []
    content_parts_log = []
    
    for chunk in chunks:
        sources.append({
            "title": chunk['title'],
            "url": chunk['url']
        })
        content_parts = {
            "chunk_id": chunk['chunk_id'],
            "title": chunk['title'],
            "url": chunk['url'],
            "content": chunk['content']
        }
        
        # Add to log array
        content_parts_log.append(content_parts)
        
        # Format for the main output
        formatted_parts = [
            f"Title: {chunk['title']}",
            f"URL: {chunk['url']}",
            f"Content: {chunk['content']}"
        ]
        formatted_content.append("\n".join(formatted_parts))

    # Save content parts log
    with open('logs/usecases_content_parts.json', 'w') as parts_log:
        json.dump(content_parts_log, parts_log, indent=2)
    print("\nContent parts saved to logs/usecases_content_parts.json")

    data = "\n---\n".join(formatted_content)

    # Load value propositions from JSON file (updated from technology-benefits.json)
    with open('temp_files/value_propositions.json', 'r') as f:
        value_props = json.load(f)

    all_results = []
    for proposition in value_props['value_propositions']:
        headline = proposition['headline']
        key_benefits = "\n".join(proposition['key_benefits'])
        supporting_features = "\n".join(proposition['supporting_features'])

        # Define the task with a prompt for Section 4
        question1 = f"""
        You are an AI assistant tasked with generating content for a sales battlecard’s 'High-Impact Use Cases' section based on a specific value proposition for {PRODUCT_NAME}. Your goal is to create three detailed use cases that demonstrate how the product delivers value, addressing customer challenges and quantifying outcomes.

        First, carefully read and analyze the provided content.

        The value proposition to focus on is: "{headline}".

        Additional context for this value proposition:
        - Key Benefits:
        {key_benefits}
        - Supporting Features:
        {supporting_features}

        Present your findings in the following JSON structure:

        <analysis>
        {{
            "topic": "{headline}",
            "use_cases": [
                {{
                    "title": "Use Case 1 Title",
                    "problem_challenge": [
                        {{"statement": "First problem or challenge statement"}},
                        {{"statement": "Second problem or challenge statement"}},
                        {{"statement": "Third problem or challenge statement"}}
                    ],
                    "solution": [
                        {{"statement": "First solution statement tied to product features"}},
                        {{"statement": "Second solution statement tied to product features"}},
                        {{"statement": "Third solution statement tied to product features"}}
                    ],
                    "value_realized": [
                        {{"statement": "First quantifiable outcome"}},
                        {{"statement": "Second quantifiable outcome"}},
                        {{"statement": "Third quantifiable outcome"}}
                    ]
                }},
                {{
                    "title": "Use Case 2 Title",
                    "problem_challenge": [
                        {{"statement": "First problem or challenge statement"}},
                        {{"statement": "Second problem or challenge statement"}},
                        {{"statement": "Third problem or challenge statement"}}
                    ],
                    "solution": [
                        {{"statement": "First solution statement tied to product features"}},
                        {{"statement": "Second solution statement tied to product features"}},
                        {{"statement": "Third solution statement tied to product features"}}
                    ],
                    "value_realized": [
                        {{"statement": "First quantifiable outcome"}},
                        {{"statement": "Second quantifiable outcome"}},
                        {{"statement": "Third quantifiable outcome"}}
                    ]
                }},
                {{
                    "title": "Use Case 3 Title",
                    "problem_challenge": [
                        {{"statement": "First problem or challenge statement"}},
                        {{"statement": "Second problem or challenge statement"}},
                        {{"statement": "Third problem or challenge statement"}}
                    ],
                    "solution": [
                        {{"statement": "First solution statement tied to product features"}},
                        {{"statement": "Second solution statement tied to product features"}},
                        {{"statement": "Third solution statement tied to product features"}}
                    ],
                    "value_realized": [
                        {{"statement": "First quantifiable outcome"}},
                        {{"statement": "Second quantifiable outcome"}},
                        {{"statement": "Third quantifiable outcome"}}
                    ]
                }}
            ]
        }}
        </analysis>

        Ensure that:
        1. Each use case has a unique, descriptive title tied to the value proposition.
        2. Problem/Challenge statements describe specific customer issues or pain points.
        3. Solution statements explain how {PRODUCT_NAME} addresses the challenges, referencing supporting features.
        4. Value Realized statements provide quantifiable outcomes (e.g., percentages, time saved) based on key benefits.
        5. All content is based on the provided context, including key benefits and supporting features.

        Output should only contain the <analysis> content.
        """
        context = data

        # Define the template
        after_rag_prompt = f"""Provide response to the request based only on the following context:
        {context}
        Additional Context: 
        - Key Benefits:
        {key_benefits}
        - Supporting Features:
        {supporting_features}
        Request: {question1}
        """

        # Invoke the chain and print results
        results = gpt_prompt(after_rag_prompt)

        print("\n########\nResults\n")
        print(results)

        # Extract JSON content and clean up the response
        json_content = results.strip()
        
        # Remove analysis tags if present
        json_content = re.sub(r'<analysis>\s*|\s*</analysis>', '', json_content)
        
        # Clean up any markdown code block markers
        json_content = re.sub(r'```json\s*|\s*```', '', json_content)
        
        # Parse and store the results
        try:
            parsed_json = json.loads(json_content.strip())
            
            # Save the results to 'temp_files/usecases.json'
            with open('temp_files/usecases.json', 'w') as file:
                json.dump(parsed_json, file, indent=4)
            print("\nResults successfully saved to temp_files/usecases.json")
            
            all_results.append(parsed_json)
            print(f"\nSuccessfully processed {headline}")
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON for {headline}: {e}")
            continue

    # Write all results to usecases.json
    with open('temp_files/usecases.json', 'w') as f:
        json.dump(all_results, f, indent=4)
    print("\nResults successfully saved to temp_files/usecases.json")

except Exception as e:
    print(f"Error occurred: {e}")