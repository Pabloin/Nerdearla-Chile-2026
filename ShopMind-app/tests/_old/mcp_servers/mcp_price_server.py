"""
mcp_price_server.py
FastMCP server exposing price_compare and user_memory tools.
Deploy to AgentCore Runtime:
  agentcore configure -e mcp_price_server.py --protocol MCP --name shopmind-price-mcp
  agentcore launch
"""

from mcp.server.fastmcp import FastMCP
import boto3, json, os

mcp = FastMCP("shopmind-price-tools")
lambda_client = boto3.client("lambda")


@mcp.tool()
async def price_compare(
    product_name: str,
    max_price_usd: float,
) -> list[dict]:
    """
    Compara precios del producto en múltiples tiendas.
    Retorna las mejores opciones dentro del presupuesto indicado.
    """
    # In production: call real APIs (Amazon PA API, MercadoLibre API, etc.)
    # For the demo: Lambda with realistic mock data
    response = lambda_client.invoke(
        FunctionName=os.environ.get("PRICE_LAMBDA", "shopmind-price-scraper"),
        Payload=json.dumps({
            "query": product_name,
            "max_price": max_price_usd,
        }),
    )
    return json.loads(response["Payload"].read())


@mcp.tool()
async def user_memory(
    user_id: str,
    action: str,        # "get" | "save"
    data: dict = None,
) -> dict:
    """
    Lee o guarda preferencias del usuario via AgentCore Memory.
    Persiste presupuesto, marcas favoritas e historial de búsqueda.
    """
    from bedrock_agentcore import AgentCoreMemory
    memory = AgentCoreMemory()

    if action == "get":
        result = await memory.retrieve(user_id)
        return result or {"budget_usd": None, "preferences": [], "history": []}
    else:
        return await memory.store(user_id, data or {})


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
