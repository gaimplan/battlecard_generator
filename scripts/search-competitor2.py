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

print("Welcome!")

# Define search queries for competitive analysis
search_queries = [
    f'"{COMPETITOR2}" product features overview capabilities',
    f'"{COMPETITOR2}" vs "{PRODUCT_NAME}" comparison differences',
    f'"{COMPETITOR2}" vs "{COMPETITOR1}" comparison differences',
    #f'"{COMPETITOR2}" pricing plans enterprise business',
    f'"{COMPETITOR2}" data sheet offer pricing',
    #f'"{COMPETITOR2}" reference architecture design guide installation guide',
    f'"{COMPETITOR2}" limitations disadvantages drawbacks',
    #f'"{COMPETITOR2}" security compliance certifications',
    #f'"{COMPETITOR2}" integration developer api',
    #f'"{COMPETITOR2}" deployment options architecture',
    f'{COMPETITOR2} "competitor comparison" "why choose"',
    f'{COMPETITOR2} "pricing objections" "value proof"',
    f'{COMPETITOR2} "core features" "integration" "ease of use"',
    #f'{COMPETITOR2} reviews "what users say" site:g2.com OR site:trustradius.com'
]

all_results = []
for query in search_queries:
    print(f"\nSearching for: {query}")
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
    'competitor': COMPETITOR2,
    'query_count': len(search_queries),
    'results': list(unique_results)
}

# Log raw Tavily results
with open('logs/COMPETITOR2_search_results.json', 'w') as log_file:
    json.dump(final_result, log_file, indent=4)
print("\nRaw Tavily results saved to logs/COMPETITOR2_search_results.json")

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
with open('temp_files/competitor2_chunks.json', 'w') as f:
    json.dump(formatted_chunks, f, indent=4)
print(f"\nFormatted chunks saved to temp_files/competitor2_chunks.json")
