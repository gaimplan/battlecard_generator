import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
import json
import re
from run import COMPETITOR2, PRODUCT_NAME, COMPETITOR1
from tavily import TavilyClient

# Load environment variables from .env file for API keys
load_dotenv()

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

print("Welcome!", flush=True)

# Define search queries for competitive analysis
search_queries = [
    f'"{COMPETITOR1}" product features overview capabilities',
    f'"{PRODUCT_NAME}" vs "{COMPETITOR1}" performance comparison',
    f'"{PRODUCT_NAME}" vs "{COMPETITOR1}" quality comparison',
    f'"{PRODUCT_NAME}" vs "{COMPETITOR1}" reliability comparison',
    f'"{PRODUCT_NAME}" vs "{COMPETITOR1}" safety comparison',
    f'"{PRODUCT_NAME}" vs "{COMPETITOR1}" ease of use comparison',
    f'"{PRODUCT_NAME}" vs "{COMPETITOR1}" features comparison',
    f'"{PRODUCT_NAME}" vs "{COMPETITOR1}" value for money comparison',
    f'"{PRODUCT_NAME}" vs "{COMPETITOR1}" customer service comparison',
    f'"{PRODUCT_NAME}" vs "{COMPETITOR1}" sustainability comparison',
    f'"{PRODUCT_NAME}" vs "{COMPETITOR1}" warranty comparison',
    f'"{COMPETITOR1}" data sheet offer pricing',
    f'"{COMPETITOR1}" limitations disadvantages drawbacks',
    f'{COMPETITOR1} "competitor comparison" "why choose"',
    f'{COMPETITOR1} "pricing objections" "value proof"',
    f'{COMPETITOR1} "core features" "integration" "ease of use"',
]

all_results = []
for query in search_queries:
    print(f"\nSearching for: {query}", flush=True)
    search_result = tavily_client.search(
        query=query,
        search_depth="advanced",
        max_results=10,  # Fewer results per query since we have multiple queries
        include_raw_content=False
    )
    all_results.extend(search_result.get('results', []))

# Deduplicate results based on URL
unique_results = {result['url']: result for result in all_results}.values()

# Create final search result structure
final_result = {
    'competitor': COMPETITOR1,
    'query_count': len(search_queries),
    'results': list(unique_results)
}

# Log raw Tavily results
with open('logs/competitor1_search_results.json', 'w') as log_file:
    json.dump(final_result, log_file, indent=4)
print("\nRaw Tavily results saved to logs/competitor1_search_results.json", flush=True)

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
        'score': result.get('score', 0.0)
    }
    formatted_chunks.append(chunk)
    chunk_id += 1

# Save formatted chunks
with open('temp_files/competitor1_chunks.json', 'w') as f:
    json.dump(formatted_chunks, f, indent=4)
print(f"\nFormatted chunks saved to temp_files/competitor1_chunks.json", flush=True)
