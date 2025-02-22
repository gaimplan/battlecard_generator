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

# Load data from chunk_summaries.json and benefits_answers.json
try:
    # Load benefits chunks
    with open('temp_files/benefits_chunks.json', 'r') as f:
        chunks = json.load(f)
    
    # Load benefits answers
    with open('temp_files/benefits_answers.json', 'r') as f:
        answers = json.load(f)
    
    # Format chunks data
    formatted_content = []
    sources = []
    content_parts_log = []
    
    # Process chunks data
    for chunk in chunks:
        sources.append({
            "title": chunk['title'],
            "url": chunk['url']
        })
        content_parts = {
            "chunk_id": chunk['chunk_id'],
            "title": chunk['title'],
            "url": chunk['url'],
            "content": chunk['content'],
            "raw_content": chunk['raw_content']
        }
        
        # Add to log array
        content_parts_log.append(content_parts)
        
        # Format for the main output
        formatted_parts = [
            f"Title: {chunk['title']}",
            f"URL: {chunk['url']}",
            f"Content: {chunk['content']}",
            f"Raw Content: {chunk['raw_content']}",
            f"Chunk ID: {chunk['chunk_id']}"
        ]
        formatted_content.append("\n".join(formatted_parts))

    # Process answers data
    for answer in answers:
        content_parts = {
            "query": answer['query'],
            "answer": answer['answer']
        }
        content_parts_log.append(content_parts)
        formatted_parts = [
            f"Query: {answer['query']}",
            f"Answer: {answer['answer']}"
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

# Create a timestamped log directory for this run
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
run_log_dir = os.path.join('logs', f'rag_valueprop_{timestamp}')
os.makedirs(run_log_dir, exist_ok=True)

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

    Carefully read and analyze the provided content about {PRODUCT_NAME}. Your task is to identify the top 3 quantifiable value propositions that make {PRODUCT_NAME} compelling to customers. Focus on measurable benefits and link them to specific features or proof points mentioned in the content.

    Here is the content to analyze:
    {entry['page_content']}

    After analyzing the content, follow these steps:

    1. Identify all quantifiable benefits of {PRODUCT_NAME} mentioned in the content (e.g., percentages, time saved, cost reductions).
    2. Select the top 3 value propositions that are most impactful.
    3. For each value proposition:
       - Provide a headline (e.g., "First value proposition headline").
       - List 3 key benefits with measurable outcomes (e.g., "First key benefit").
       - List 3 supporting features or proof points (e.g., "First supporting feature").
    4. Include all relevant sources from the content in the sources array.

    Present your findings in the following format:

    <value_propositions>
    {value_propositions_template}
    </value_propositions>

    Ensure the output is detailed, quantifiable, and directly tied to the content provided. Do not make up or guess facts, figures or words. Replace the generic placeholders in the template (e.g., "First value proposition headline", "First key benefit") with your specific findings. Output should only contain the <value_propositions> content.
    """

    # Define the prompt with context
    after_rag_prompt = f"""Provide response to the request based only on the following context:
    {entry['page_content']}
    Request: {intro_prompt}
    """

    # Log the input data and prompt
    input_log = {
        "timestamp": datetime.now().isoformat(),
        "input_data": entry['page_content'],
        "prompt": after_rag_prompt,
        "sources": entry.get('sources', [])
    }
    with open(os.path.join(run_log_dir, 'input_data.json'), 'w') as f:
        json.dump(input_log, f, indent=4)

    # Invoke the chain and print results
    results = gpt_prompt(after_rag_prompt)

    # Log the raw LLM response
    response_log = {
        "timestamp": datetime.now().isoformat(),
        "raw_response": results
    }
    with open(os.path.join(run_log_dir, 'llm_response.json'), 'w') as f:
        json.dump(response_log, f, indent=4)

    print("\n########\nResults\n")
    print(results)

    # Extract JSON content from between tags and parse it
    json_start = results.find("<value_propositions>")
    json_end = results.find("</value_propositions>")
    
    if json_start == -1 or json_end == -1:
        error_msg = "Error: Could not find value_propositions tags in response"
        print(error_msg)
        # Log the error
        with open(os.path.join(run_log_dir, 'error.log'), 'w') as f:
            f.write(f"{datetime.now().isoformat()}: {error_msg}\n")
        sys.exit(1)
        
    json_content = results[json_start + len("<value_propositions>"):json_end].strip()
    
    try:
        # Parse the JSON directly
        parsed_json = json.loads(json_content)
        
        # Save the parsed results
        output_log = {
            "timestamp": datetime.now().isoformat(),
            "parsed_results": parsed_json
        }
        with open(os.path.join(run_log_dir, 'parsed_results.json'), 'w') as f:
            json.dump(output_log, f, indent=4)
        
        # Save to the main output file
        with open('temp_files/value_propositions.json', 'w') as file:
            json.dump(parsed_json, file, indent=4)
        print("\nResults successfully saved to temp_files/value_propositions.json")
        
    except json.JSONDecodeError as e:
        error_msg = f"\nError parsing JSON: {str(e)}\nRaw content that failed to parse:\n{json_content}"
        print(error_msg)
        # Log the error
        with open(os.path.join(run_log_dir, 'error.log'), 'w') as f:
            f.write(f"{datetime.now().isoformat()}: {error_msg}\n")
        sys.exit(1)

    print(f"Results and logs saved to {run_log_dir}")