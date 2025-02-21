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
    with open('logs/action_plan_content_parts.json', 'w') as parts_log:
        json.dump(content_parts_log, parts_log, indent=2)
    print("\nContent parts saved to logs/action_plan_content_parts.json")

    context = "\n---\n".join(formatted_content)

    # Define the action plan template for Section 7
    action_plan_template = """
    {
        "action_plan": {
            "value_that_closes": [
                "First key benefit",
                "Second key benefit",
                "Third key benefit",
                "Fourth key benefit",
                "Fifth key benefit"
            ],
            "next_steps": [
                "First actionable step",
                "Second actionable step",
                "Third actionable step",
                "Fourth actionable step",
                "Fifth actionable step"
            ],
            "sales_playbook": [
                "First sales strategy",
                "Second sales strategy",
                "Third sales strategy",
                "Fourth sales strategy",
                "Fifth sales strategy"
            ]
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
    You are tasked with analyzing provided content about {PRODUCT_NAME} to create an action plan for sealing the deal in a sales battlecard. This task aims to identify the most compelling benefits, actionable next steps, and sales strategies to close the sale effectively.

    Carefully read and analyze the provided content about {PRODUCT_NAME}. Focus on information that highlights the product’s strengths, benefits, competitive advantages over {COMPETITOR1} and {COMPETITOR2}, and any clues about customer needs or sales opportunities.

    Here is the content to analyze:
    {context}

    After analyzing the content, follow these steps:

    1. Identify the top 5 benefits that would convince a customer to choose {PRODUCT_NAME} (e.g., measurable outcomes, unique features). These will form the 'value_that_closes' section.
    2. Develop 5 actionable next steps to move the sale forward (e.g., demos, trials, specific engagements). These will form the 'next_steps' section.
    3. Create 5 sales strategies to guide the sales team (e.g., discovery tactics, value emphasis, competitive positioning). These will form the 'sales_playbook' section.
    4. Include all relevant sources from the content in the sources array.

    Present your findings in the following format:

    <action_plan>
    {action_plan_template}
    </action_plan>

    Ensure that:
    1. All entries are directly based on or reasonably inferred from the provided content.
    2. Do not introduce external information not supported by the text.
    3. Each section (value_that_closes, next_steps, sales_playbook) must contain exactly 5 items.
    4. Benefits should be compelling and quantifiable where possible, steps should be actionable, and strategies should be practical for sales execution.

    Output should only contain the <action_plan> content.
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
    
    # Remove action_plan tags if present
    json_content = re.sub(r'<action_plan>\s*|\s*</action_plan>', '', json_content)
    
    # Clean up any markdown code block markers
    json_content = re.sub(r'```json\s*|\s*```', '', json_content)
    json_content = re.sub(r'^\s*xml\s*', '', json_content)

    try:
        # Parse and store the results
        parsed_json = json.loads(json_content.strip())
        
        # Save the results to 'temp_files/action_plan.json'
        with open('temp_files/action_plan.json', 'w') as file:
            json.dump(parsed_json, file, indent=4)
        print("\nResults successfully saved to temp_files/action_plan.json")
    except json.JSONDecodeError as e:
        print(f"\nError parsing JSON: {e}")
        print("Raw content that failed to parse:")
        print(json_content)

except Exception as e:
    print(f"Error occurred during file operations: {e}")