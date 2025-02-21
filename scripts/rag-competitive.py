import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
import json
from run import PRODUCT_NAME, COMPETITOR1, COMPETITOR2
from langchain_google_genai import GoogleGenerativeAI
from datetime import datetime

# Load environment variables from .env file for API keys
load_dotenv()

# Ensure directories exist
os.makedirs('logs', exist_ok=True)
os.makedirs('temp_files', exist_ok=True)
os.makedirs('output', exist_ok=True)

print("Welcome!")

# Initialize model
model_local = GoogleGenerativeAI(
    model="gemini-2.0-flash",
    verbose=True,
    temperature=0.2,
    google_api_key=os.environ.get("GOOGLE_API_KEY")
)

def gpt_prompt(prompt):
    try:
        print(f"Sending prompt of length: {len(prompt)} characters")
        response = model_local.invoke(prompt)
        if response:
            return response.strip()
        return ""
    except Exception as e:
        error_msg = str(e)
        print(f"\nError Type: {type(e).__name__}")
        print(f"Error Message: {error_msg}")
        if "429" in error_msg or "rate limit" in error_msg.lower():
            print("\nRATE LIMIT ERROR DETECTED - Too Many Requests")
        return ""

# Load and combine documents
print("\nLoading documents...")
all_documents = []
try:
    # Load competitor1 summaries
    with open('temp_files/competitor1_chunks.json', 'r') as f:
        competitor1_data = json.load(f)
        for chunk in competitor1_data:
            content = chunk.get('notes', '') + "\nTopics:\n" + chunk.get('topics', '')
            all_documents.append({"page_content": content, "metadata": {"source": "competitor1"}})
    
    # Load competitor2 summaries
    with open('temp_files/competitor2_chunks.json', 'r') as f:
        competitor2_data = json.load(f)
        for chunk in competitor2_data:
            content = chunk.get('notes', '') + "\nTopics:\n" + chunk.get('topics', '')
            all_documents.append({"page_content": content, "metadata": {"source": "competitor2"}})
    
    # Load benefits summaries
    with open('temp_files/benefits_chunks.json', 'r') as f:
        benefits_data = json.load(f)
        for chunk in benefits_data:
            content = chunk.get('notes', '') + "\nTopics:\n" + chunk.get('topics', '')
            all_documents.append({"page_content": content, "metadata": {"source": "benefits"}})
    
    print(f"Loaded {len(all_documents)} total documents")
except Exception as e:
    print(f"Error loading documents: {str(e)}")
    raise

# Load value propositions
try:
    with open('temp_files/value_propositions.json', 'r') as f:
        value_props = json.load(f)
    
    # Build value props content without using backslashes in f-strings
    value_props_sections = []
    for vp in value_props['value_propositions']:
        # Create the headline section
        headline = f"Headline: {vp['headline']}"
        
        # Create the key benefits section
        benefits = "Key Benefits:"
        for benefit in vp['key_benefits']:
            benefits += f"\n{benefit}"
            
        # Create the supporting features section
        features = "Supporting Features:"
        for feature in vp['supporting_features']:
            features += f"\n{feature}"
            
        # Combine all sections
        section = f"{headline}\n{benefits}\n{features}"
        value_props_sections.append(section)
    
    # Join all sections with double newlines
    value_props_content = "\n\n".join(value_props_sections)
except Exception as e:
    print(f"Error loading value_propositions.json: {str(e)}")
    value_props_content = "No value propositions data available."

# Log the documents content
print("\nSaving context to log file...")
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = os.path.join('logs', f"rag_competitive_context_{timestamp}.json")
with open(log_file, 'w') as f:
    json.dump(all_documents, f, indent=2)
print(f"Context saved to {log_file}")

# Combine all document content
print("\nPreparing combined context...")
combined_context = "\n\n".join([doc["page_content"] for doc in all_documents])
print(f"Combined context length: {len(combined_context)} characters")

# Define the task with a prompt
question1 = f"""You are tasked with creating a competitive analysis for {PRODUCT_NAME} against {COMPETITOR1} and {COMPETITOR2} for a sales battlecard's 'Competitive Analysis' section.

Carefully analyze the provided content and generate the following:

Present your findings in this JSON structure:

<analysis>
{{
    "positioning_vs_{COMPETITOR1.lower()}": {{
        "statement": "Positioning statement comparing {PRODUCT_NAME} to {COMPETITOR1}",
        "advantages": [
            {{"statement": "First advantage"}},
            {{"statement": "Second advantage"}},
            {{"statement": "Third advantage"}}
        ]
    }},
    "positioning_vs_{COMPETITOR2.lower()}": {{
        "statement": "Positioning statement comparing {PRODUCT_NAME} to {COMPETITOR2}",
        "advantages": [
            {{"statement": "First advantage"}},
            {{"statement": "Second advantage"}},
            {{"statement": "Third advantage"}}
        ]
    }},
    "competitive_matrix": [
        {{
            "feature": "Feature 1",
            "scores": [
                {{"product": "{PRODUCT_NAME}", "score": "Excellent/Good/Fair/Poor", "justification": "Reason for score"}},
                {{"product": "{COMPETITOR1}", "score": "Excellent/Good/Fair/Poor", "justification": "Reason for score"}},
                {{"product": "{COMPETITOR2}", "score": "Excellent/Good/Fair/Poor", "justification": "Reason for score"}}
            ],
            "advantage": "Advantage statement for {PRODUCT_NAME}"
        }}
    ],
    "win_themes": [
        {{"statement": "First win theme"}},
        {{"statement": "Second win theme"}},
        {{"statement": "Third win theme"}}
    ]
}}
</analysis>

Ensure that:
1. Include 3-5 key features in the competitive matrix.
2. Scores are qualitative (Excellent, Good, Fair, Poor) with detailed justifications.
3. Positioning statements highlight {PRODUCT_NAME}'s unique strengths.
4. Advantages are specific and tied to features or benefits.
5. Win themes emphasize {PRODUCT_NAME}'s superiority over both competitors.
6. All content is based on the provided context and value propositions.
7. Assessments are objective and fair.

Output should only contain the <analysis> content."""

# Define the template
after_rag_prompt = f"""Provide response to the request based only on the following context:
{combined_context}
Additional Context (Value Propositions for {PRODUCT_NAME}):
{value_props_content}
Request: {question1}
"""

print("\nGenerating competitive analysis...")
print("\nSending request to model...")
# Invoke the chain and print results
try:
    results = gpt_prompt(after_rag_prompt)
    print("\nReceived response from model")
except Exception as e:
    print(f"\nError during model invocation: {str(e)}")
    raise

print("\n########\nResults\n")
print(results)

# Extract proper JSON substring by locating the first '{' and the last '}'
start_index = results.find('{')
end_index = results.rfind('}')
if start_index == -1 or end_index == -1:
    print("Error: JSON block not found in the response")
    sys.exit(1)
json_content = results[start_index:end_index+1]

try:
    # Parse and store the results
    parsed_json = json.loads(json_content)
    
    # Save the results to 'temp_files/competitive.json'
    with open('temp_files/competitive.json', 'w') as file:
        json.dump(parsed_json, file, indent=4)
    print("\nResults successfully saved to temp_files/competitive.json")
except json.JSONDecodeError as e:
    print(f"\nError parsing JSON: {e}")
    print("\nProblematic JSON content:")
    print(json_content)
    # Write the problematic content to a file for debugging
    with open('temp_files/problematic_json.txt', 'w') as f:
        f.write(json_content)