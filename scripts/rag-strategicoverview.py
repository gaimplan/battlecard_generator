import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
import json
import re
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
    with open('logs/strategic_overview_content_parts.json', 'w') as parts_log:
        json.dump(content_parts_log, parts_log, indent=2)
    print("\nContent parts saved to logs/strategic_overview_content_parts.json")

    context = "\n---\n".join(formatted_content)

    # Include competitive and value propositions data in the context
    import json

    try:
        with open('temp_files/competitive.json', 'r') as competitive_file:
            competitive_data = json.load(competitive_file)
    except Exception as e:
        competitive_data = {}
        print(f"Error loading competitive.json: {e}")

    try:
        with open('temp_files/value_propositions.json', 'r') as vp_file:
            value_prop_data = json.load(vp_file)
    except Exception as e:
        value_prop_data = {}
        print(f"Error loading value_propositions.json: {e}")

    context_dict = {
        'benefits': context,
        'competitive': competitive_data,
        'value_propositions': value_prop_data
    }

    context = json.dumps(context_dict, indent=4)

    # Define the strategic overview template for Section 1
    strategic_overview_template = """
    {
        "strategic_overview": {
            "elevator_pitch": "Concise summary of the product’s value",
            "target_customer_profile": {
                "personas": [
                    {
                        "role": "First persona role",
                        "key_goal": "Primary goal for first persona",
                        "pain_points": [
                            "First pain point",
                            "Second pain point",
                            "Third pain point"
                        ]
                    },
                    {
                        "role": "Second persona role",
                        "key_goal": "Primary goal for second persona",
                        "pain_points": [
                            "First pain point",
                            "Second pain point",
                            "Third pain point"
                        ]
                    },
                    {
                        "role": "Third persona role",
                        "key_goal": "Primary goal for third persona",
                        "pain_points": [
                            "First pain point",
                            "Second pain point",
                            "Third pain point"
                        ]
                    }
                ],
                "primary_pain_point": "Overarching customer problem"
            },
            "market_context": "Brief market trend statement"
        },
        "sources": [
            {
                "title": "Source title",
                "url": "Source URL"
            }
        ]
    }
    """

    # Define the task with a prompt
    question1 = f""" 
    You are tasked with analyzing provided content about {PRODUCT_NAME} to create a strategic overview for a sales battlecard. This task aims to summarize the product’s value, define its target customers, and provide market context based on the content.

    Carefully read and analyze the provided content about {PRODUCT_NAME}. Focus on information that highlights the product’s purpose, benefits, competitive advantages over {COMPETITOR1} and {COMPETITOR2}, customer challenges, and any market-related insights.

    Here is the content to analyze:
    {context}

    After analyzing the content, follow these steps:

    1. Craft a concise 1-2 sentence elevator pitch summarizing {PRODUCT_NAME}’s value, including what it does, its key benefit, and a unique differentiator.
    2. Identify or infer 3 target customer personas:
       - Assign a role (e.g., IT Manager, Business Leader, End User).
       - Define 1 key goal per persona based on their needs or benefits mentioned.
       - List 3 pain points per persona based on challenges addressed by {PRODUCT_NAME}.
    3. Summarize the primary pain point that {PRODUCT_NAME} solves across these personas.
    4. Provide a brief market context statement (1-2 sentences) about the industry or trends relevant to {PRODUCT_NAME}. If possible, include a statistic or source from the content; otherwise, infer a plausible trend.
    5. Include all relevant sources from the content in the sources array.

    Present your findings in the following format:

    <strategic_overview>
    {strategic_overview_template}
    </strategic_overview>

    Ensure that:
    1. All entries are directly based on or reasonably inferred from the provided content.
    2. Do not introduce external information not supported by the text.
    3. The elevator pitch is concise (1-2 sentences), each persona has 1 goal and 3 pain points, and the market context is brief (1-2 sentences).
    4. If specific details (e.g., personas, market trends) are missing, infer plausible ones based on the content’s benefits or context.

    Output should only contain the <strategic_overview> content.
    """

    # Define the prompt with context
    after_rag_prompt = f"""Provide response to the request based only on the following context:
    {context}
    Request: {question1}
    """

    # Invoke the chain and print results
    results = gpt_prompt(after_rag_prompt)

    print("\n########\nResults\n")
    print(results)

    # Extract JSON content and clean up the response
    json_content = results.strip()
    
    # Remove strategic_overview tags if present
    json_content = re.sub(r'<strategic_overview>\s*|\s*</strategic_overview>', '', json_content)
    
    # Clean up any markdown code block markers or xml
    json_content = re.sub(r'```json\s*|\s*```', '', json_content)
    json_content = re.sub(r'^\s*xml\s*', '', json_content)

    try:
        # Parse and store the results
        parsed_json = json.loads(json_content.strip())
        
        # Save the results to 'temp_files/strategic_overview.json'
        with open('temp_files/strategic_overview.json', 'w') as file:
            json.dump(parsed_json, file, indent=4)
        print("\nResults successfully saved to temp_files/strategic_overview.json")
    except json.JSONDecodeError as e:
        print(f"\nError parsing JSON: {e}")
        print("Raw content that failed to parse:")
        print(json_content)

except Exception as e:
    print(f"Error occurred during file operations: {e}")