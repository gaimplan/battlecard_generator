import os
import sys
# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from datetime import datetime
from dotenv import load_dotenv
from run import PRODUCT_NAME, COMPETITOR1, COMPETITOR2
from langchain_google_genai import GoogleGenerativeAI

# Load environment variables from .env file for API keys
load_dotenv()

model_local = GoogleGenerativeAI(
    model="gemini-2.0-flash",
    verbose=True,
    temperature=0.2,
    google_api_key=os.environ.get("GOOGLE_API_KEY")
)

# Ensure directories exist
os.makedirs('logs', exist_ok=True)
os.makedirs('temp_files', exist_ok=True)
os.makedirs('output', exist_ok=True)

print("Welcome!")

# Load data from chunk_summaries.json
try:
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
            f"Chunk ID: {chunk['chunk_id']}"
        ]
        formatted_content.append("\n".join(formatted_parts))

    # Save content parts log
    with open('logs/benefits_content_parts.json', 'w') as parts_log:
        json.dump(content_parts_log, parts_log, indent=2)
    print("\nContent parts saved to logs/benefits_content_parts.json")

    data = [{
        "page_content": "\n---\n".join(formatted_content),
        "sources": sources
    }]

    # Log formatted data
    with open('logs/benefits_formatted_data.json', 'w') as log_file:
        json.dump(data, log_file, indent=4)
    print("\nFormatted data saved to logs/benefits_formatted_data.json")

except Exception as e:
    print(f"Error loading or processing data: {e}")
    exit(1)

def gpt_prompt(prompt):
    try:
        response = model_local.invoke(prompt)
        if response:
            return response.strip()
        return ""
    except Exception as e:
        print(f"Error occurred: {e}")
        return ""

for entry in data:
    # Create the value propositions template for Section 2
    value_propositions_template = """
    {
        "value_propositions": [
            {
                "headline": "First value proposition headline",
                "key_benefits": [
                    "First key benefit",
                    "Second key benefit",
                    "Third key benefit"
                ],
                "supporting_features": [
                    "First supporting feature",
                    "Second supporting feature",
                    "Third supporting feature"
                ]
            },
            {
                "headline": "Second value proposition headline",
                "key_benefits": [
                    "First key benefit",
                    "Second key benefit",
                    "Third key benefit"
                ],
                "supporting_features": [
                    "First supporting feature",
                    "Second supporting feature",
                    "Third supporting feature"
                ]
            },
            {
                "headline": "Third value proposition headline",
                "key_benefits": [
                    "First key benefit",
                    "Second key benefit",
                    "Third key benefit"
                ],
                "supporting_features": [
                    "First supporting feature",
                    "Second supporting feature",
                    "Third supporting feature"
                ]
            }
        ],
        "sources": [
            {
                "title": "Source title",
                "url": "Source URL"
            }
        ]
    }
    """

    # Define the task with a prompt
    intro_prompt = f"""
    Based on the provided content, you will be analyzing content about {PRODUCT_NAME} to identify its top quantifiable value propositions for a battlecard.

    Carefully read and analyze the provided content about {PRODUCT_NAME}. Your task is to identify the top 3 quantifiable value propositions that make {PRODUCT_NAME} compelling to customers. Focus on measurable benefits (e.g., cost reduction, efficiency gains, reliability improvements) and link them to specific features or proof points mentioned in the content.

    Here is the content to analyze:
    {entry['page_content']}

    After analyzing the content, follow these steps:

    1. Identify all quantifiable benefits of {PRODUCT_NAME} mentioned in the content (e.g., percentages, time saved, cost reductions).
    2. Select the top 3 value propositions that are most impactful, aligning them with common business goals like reducing costs, increasing efficiency, or enhancing reliability.
    3. For each value proposition:
       - Provide a headline (e.g., "First value proposition headline").
       - List 3 key benefits with measurable outcomes (e.g., "First key benefit").
       - List 3 supporting features or proof points (e.g., "First supporting feature").
    4. Include all relevant sources from the content in the sources array.

    Present your findings in the following format:

    <value_propositions>
    {value_propositions_template}
    </value_propositions>

    Ensure the output is concise, quantifiable, and directly tied to the content provided. If specific metrics or proof points are missing, infer reasonable examples based on the context and note them as inferred. Replace the generic placeholders in the template (e.g., "First value proposition headline", "First key benefit") with your specific findings. Output should only contain the <value_propositions> content.
    """

    # Define the prompt with context
    after_rag_prompt = f"""Provide response to the request based only on the following context:
    {entry['page_content']}
    Request: {intro_prompt}
    """

    # Invoke the chain and print results
    results = gpt_prompt(after_rag_prompt)

    print("\n########\nResults\n")
    print(results)

    # Extract JSON content from between tags and parse it
    json_start = results.find("<value_propositions>")
    json_end = results.find("</value_propositions>")
    
    if json_start == -1 or json_end == -1:
        print("Error: Could not find value_propositions tags in response")
        sys.exit(1)
        
    json_content = results[json_start + len("<value_propositions>"):json_end].strip()
    
    # Debug output
    print("\nJSON Content to parse:")
    print(json_content)
    
    try:
        # Parse the JSON directly
        parsed_json = json.loads(json_content)
        
        # Save the results to 'temp_files/value_propositions.json'
        with open('temp_files/value_propositions.json', 'w') as file:
            json.dump(parsed_json, file, indent=4)
        print("\nResults successfully saved to temp_files/value_propositions.json")
        
    except json.JSONDecodeError as e:
        print(f"\nError parsing JSON: {str(e)}")
        print("Raw content that failed to parse:")
        print(json_content)
        sys.exit(1)

    print("Results saved to temp_files/value_propositions.json")