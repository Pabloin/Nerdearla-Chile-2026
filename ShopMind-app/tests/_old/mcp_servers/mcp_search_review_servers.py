"""
mcp_search_server.py  — MCP tool: web_search
mcp_review_server.py  — MCP tool: fetch_reviews

Both deployed on AgentCore Runtime, registered as targets in AgentCore Gateway.
"""

# ════════════════════════════════════════════════════════════
# mcp_search_server.py
# ════════════════════════════════════════════════════════════
from mcp.server.fastmcp import FastMCP
import httpx, os

mcp_search = FastMCP("shopmind-search-tools")


@mcp_search.tool()
async def web_search(query: str, max_results: int = 10) -> list[dict]:
    """
    Busca productos en la web usando DuckDuckGo Instant Answer API.
    Retorna lista de resultados con título, descripción y URL.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_html": 1, "no_redirect": 1},
        )
        data = response.json()

    results = []
    for item in data.get("RelatedTopics", [])[:max_results]:
        if "Text" in item:
            results.append({
                "title": item.get("Text", "")[:100],
                "url": item.get("FirstURL", ""),
            })
    return results


# ════════════════════════════════════════════════════════════
# mcp_review_server.py
# ════════════════════════════════════════════════════════════
mcp_reviews = FastMCP("shopmind-review-tools")


@mcp_reviews.tool()
async def fetch_reviews(
    product_name: str,
    focus_audience: str = "general",  # e.g. "estudiantes", "gamers"
) -> dict:
    """
    Obtiene y analiza reseñas del producto.
    focus_audience filtra reseñas relevantes para el tipo de usuario.
    """
    import boto3, json

    lambda_client = boto3.client("lambda")
    response = lambda_client.invoke(
        FunctionName=os.environ.get("REVIEWS_LAMBDA", "shopmind-review-analyzer"),
        Payload=json.dumps({
            "product": product_name,
            "audience": focus_audience,
        }),
    )
    return json.loads(response["Payload"].read())


if __name__ == "__main__":
    import sys
    if "search" in sys.argv:
        mcp_search.run(transport="streamable-http", host="0.0.0.0", port=8000)
    else:
        mcp_reviews.run(transport="streamable-http", host="0.0.0.0", port=8000)
