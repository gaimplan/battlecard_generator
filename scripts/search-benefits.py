import os
import sys
import time
from dotenv import load_dotenv
import json
from tavily import TavilyClient

# Append parent directory to sys.path for module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from run import PRODUCT_NAME

# Load environment variables
load_dotenv()

# Initialize Tavily client
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

print("Welcome!", flush=True)

# Initialize answers collection
answers = []

# Define search queries
search_queries = [
f'"{PRODUCT_NAME}" overview',
f'"{PRODUCT_NAME}" features and benefits',
f'"{PRODUCT_NAME}" performance and reliability',
f'"{PRODUCT_NAME}" quality and durability',
f'"{PRODUCT_NAME}" safety and security',
f'"{PRODUCT_NAME}" user experience',
f'"{PRODUCT_NAME}" pricing and value',
f'"{PRODUCT_NAME}" customer service reviews',
f'"{PRODUCT_NAME}" warranty coverage',
f'"{PRODUCT_NAME}" sustainability',
f'"{PRODUCT_NAME}" vs competitors'
]

all_results = []
for query in search_queries:
    print(f"\nSearching for: {query}", flush=True)
    try:
        # Fetch search results with raw content
        search_result = tavily_client.search(
            query=query,
            search_depth="advanced",
            include_answer= "advanced",
            max_results=5,  
            include_raw_content=True  # Fetch full raw content
        )
        results = search_result.get('results', [])
        all_results.extend(results)
        
        # Store answer with query
        answers.append({
            'query': query,
            'answer': search_result.get('answer', '')
        })
        
        # Log raw response for debugging
        with open(f'logs/raw_response_{query[:30].replace(" ", "_")}.json', 'w') as log_file:
            json.dump(search_result, log_file, indent=4)
        
        # Add delay to avoid rate limiting
        time.sleep(1.5)
    except Exception as e:
        print(f"Error with query '{query}': {e}", flush=True)

# Deduplicate results based on URL
unique_results = {result['url']: result for result in all_results}.values()

# Create final search result structure
final_result = {
    'product': PRODUCT_NAME,
    'query_count': len(search_queries),
    'results': list(unique_results)
}

# Save raw Tavily results
with open('logs/benefits_search_results.json', 'w') as log_file:
    json.dump(final_result, log_file, indent=4)
print("\nRaw Tavily results saved to logs/benefits_search_results.json", flush=True)

# Process and format the results for chunking
formatted_chunks = []
chunk_id = 1

for result in unique_results:
    content = result.get('content', '')
    raw_content = result.get('raw_content', '')
    
    # Use raw_content if content is too short (e.g., < 100 chars)
    if len(content) < 100 and raw_content:
        content = raw_content[:1000]  # Truncate raw content to manageable size
    
    chunk = {
        'chunk_id': chunk_id,
        'title': result.get('title', ''),
        'url': result.get('url', ''),
        'content': content,
        'raw_content': raw_content,  # Store full raw content
        'score': result.get('score', 0.0)
    }
    formatted_chunks.append(chunk)
    chunk_id += 1

# Save formatted chunks
with open('temp_files/benefits_chunks.json', 'w') as f:
    json.dump(formatted_chunks, f, indent=4)
print(f"\nFormatted chunks saved to temp_files/benefits_chunks.json", flush=True)

# Save answers to JSON
os.makedirs('temp_files', exist_ok=True)
with open('temp_files/benefits_answers.json', 'w') as f:
    json.dump(answers, f, indent=4)
print(f"\nAnswer data saved to temp_files/benefits_answers.json", flush=True)