import os
import requests

API_KEY = os.getenv("S2_API_KEY")
assert API_KEY, "Need to set `S2_API_KEY` in environment variables"

def search_semantic_scholar(query: str, limit: int = 5):
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": limit,
        "fields": "title,authors,year,abstract,citationCount,openAccessPdf"
    }
    headers = {"X-API-KEY": API_KEY}
    resp = requests.get(url, params=params, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()

if __name__ == "__main__":
    query = "reasoning via video"
    data = search_semantic_scholar(query)
    print(f"Total: {data.get('total')}")
    for i, p in enumerate(data.get("data", []), 1):
        print(f"[{i}] {p.get('title')}")
        print(f"    year={p.get('year')}, cites={p.get('citationCount')}")
        print(f"    pdf={p.get('openAccessPdf', {}).get('url')}")