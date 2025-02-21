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
    with open('logs/objection_content_parts.json', 'w') as parts_log:
        json.dump(content_parts_log, parts_log, indent=2)
    print("\nContent parts saved to logs/objection_content_parts.json")

    context = "\n---\n".join(formatted_content)

    # Define the objection handling template for Section 6
    objection_handling_template = """
    {
        "objections": [
            {
                "objection_name": "First common objection",
                "response": [
                    "First response point",
                    "Second response point",
                    "Third response point"
                ],
                "evidence": [
                    "First evidence point",
                    "Second evidence point",
                    "Third evidence point"
                ]
            },
            {
                "objection_name": "Second common objection",
                "response": [
                    "First response point",
                    "Second response point",
                    "Third response point"
                ],
                "evidence": [
                    "First evidence point",
                    "Second evidence point",
                    "Third evidence point"
                ]
            },
            {
                "objection_name": "Third common objection",
                "response": [
                    "First response point",
                    "Second response point",
                    "Third response point"
                ],
                "evidence": [
                    "First evidence point",
                    "Second evidence point",
                    "Third evidence point"
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
    question1 = f""" 
    You are tasked with analyzing provided content and identifying the top 3 customer objections for {PRODUCT_NAME} along with appropriate objection-handling responses and evidence. This task aims to improve customer service and sales techniques by preparing effective responses to common objections for a battlecard.

    Carefully read and analyze the provided content about {PRODUCT_NAME}. Pay close attention to any information that reveals potential customer concerns, hesitations, or objections regarding the product, service, or company. If explicit objections are not mentioned, infer plausible objections based on the context (e.g., cost, competition, priority) and how {PRODUCT_NAME} addresses related challenges.

    Here is the content to analyze:
    {context}

    After analyzing the content, follow these steps:

    1. Identify or infer the top 3 customer objections related to {PRODUCT_NAME} (e.g., cost, preference for {COMPETITOR1} or {COMPETITOR2}, or lack of urgency).
    2. For each objection:
       - Provide a concise objection name (e.g., "First common objection").
       - List 3 response points that address the objection directly (e.g., "First response point").
       - List 3 evidence points that support the responses with proof from the content (e.g., "First evidence point"). If specific evidence is missing, infer reasonable examples based on the content and note them as inferred.
    3. Include all relevant sources from the content in the sources array.

    Present your findings in the following format:

    <objection_handling>
    {objection_handling_template}
    </objection_handling>

    Ensure that:
    1. All responses and evidence are directly based on or reasonably inferred from the provided content.
    2. Do not introduce external information not supported by the text.
    3. If fewer than three distinct objections can be identified, include only those that can be derived from the content.
    4. Each objection must have 3 response points and 3 evidence points.
    5. Responses should be concise yet effective in addressing the objection, and evidence should provide tangible support.

    Output should only contain the <objection_handling> content.
    """

    # Define the template
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
    
    # Remove objection_handling tags if present
    json_content = re.sub(r'<objection_handling>\s*|\s*</objection_handling>', '', json_content)
    
    # Clean up any markdown code block markers
    json_content = re.sub(r'```json\s*|\s*```', '', json_content)
    
    try:
        # Parse and store the results
        parsed_json = json.loads(json_content.strip())
        
        # Save the results to 'temp_files/objection_handling.json'
        with open('temp_files/objection_handling.json', 'w') as file:
            json.dump(parsed_json, file, indent=4)
        print("\nResults successfully saved to temp_files/objection_handling.json")
    except json.JSONDecodeError as e:
        print(f"\nError parsing JSON: {e}")
        print("Raw content that failed to parse:")
        print(json_content)

except Exception as e:
    print(f"Error occurred during file operations: {e}")