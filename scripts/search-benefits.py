import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
import json
import re
from run import PRODUCT_NAME
from tavily import TavilyClient

# Load environment variables from .env file for API keys
load_dotenv()

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

print("Welcome!", flush=True)

# Define search queries for benefits analysis
search_queries = [
    f'"{PRODUCT_NAME}" features capabilities benefits overview',
    f'"{PRODUCT_NAME}" data sheet offer pricing',
    #f'"{PRODUCT_NAME}" reference architecture design guide installation guide',
    f'"{PRODUCT_NAME}" technology advantages benefits',
    #f'"{PRODUCT_NAME}" business value ROI benefits',
    #f'"{PRODUCT_NAME}" technical architecture infrastructure',
    f'"{PRODUCT_NAME}" security reliability performance',
    #f'"{PRODUCT_NAME}" scalability flexibility integration',
    f'"{PRODUCT_NAME}" user experience interface benefits',
    #f'"{PRODUCT_NAME}" deployment maintenance support',
    #f'{PRODUCT_NAME} "key benefits" "customer wins" site:*.com -inurl:(signup login)',
    f'{PRODUCT_NAME} "competitor comparison" "why choose"',
    f'{PRODUCT_NAME} "pricing objections" "value proof"',
    f'{PRODUCT_NAME} "core features" "integration" "ease of use"',
    #f'{PRODUCT_NAME} reviews "what users say" site:g2.com OR site:trustradius.com'
]

all_results = []
for query in search_queries:
    print(f"\nSearching for: {query}", flush=True)
    search_result = tavily_client.search(
        query=query,
        search_depth="advanced",
        max_results=10,  # Fewer results per query since we have multiple queries
        search_type="comprehensive",
        include_raw_content=False
    )
    all_results.extend(search_result.get('results', []))

# Deduplicate results based on URL
unique_results = {result['url']: result for result in all_results}.values()

# Create final search result structure
final_result = {
    'product': PRODUCT_NAME,
    'query_count': len(search_queries),
    'results': list(unique_results)
}

# Log raw Tavily results
with open('logs/benefits_search_results.json', 'w') as log_file:
    json.dump(final_result, log_file, indent=4)
print("\nRaw Tavily results saved to logs/benefits_search_results.json", flush=True)

# Process and format the results for chunking
formatted_chunks = []
chunk_id = 1

for result in unique_results:
    # Create chunk
    chunk = {
        'chunk_id': chunk_id,
        'title': result.get('title', ''),
        'url': result.get('url', ''),
        'content': result.get('content', ''),
        'raw_content': result.get('raw_content', ''),
        'score': result.get('score', 0.0)
    }
    formatted_chunks.append(chunk)
    chunk_id += 1

# Save formatted chunks
with open('temp_files/benefits_chunks.json', 'w') as f:
    json.dump(formatted_chunks, f, indent=4)
print(f"\nFormatted chunks saved to temp_files/benefits_chunks.json", flush=True)
