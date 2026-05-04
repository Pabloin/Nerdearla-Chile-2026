"""
ShopMind backend Lambda
POST /invoke  →  runs Strands agent directly  →  returns JSON response
No AgentCore Runtime cold start issue.
"""
import json, boto3, uuid

REGION     = "us-east-1"
TOOLS_LAMBDA = "shopmind-tools"

CORS = {
    "Access-Control-Allow-Origin":  "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}

_lambda_client = boto3.client("lambda", region_name=REGION)
_agent = None


def _call_tool(tool_name: str, **kwargs) -> str:
    resp = _lambda_client.invoke(
        FunctionName=TOOLS_LAMBDA,
        Payload=json.dumps({"tool": tool_name, **kwargs}),
    )
    result = json.loads(resp["Payload"].read())
    return json.dumps(result, ensure_ascii=False)


def _get_agent():
    global _agent
    if _agent is None:
        from strands import Agent, tool

        @tool
        def web_search(query: str, max_results: int = 10) -> str:
            """Busca productos en la web. Retorna lista de resultados con titulo y URL."""
            return _call_tool("web_search", query=query, max_results=max_results)

        @tool
        def price_compare(product_name: str, max_price_usd: float) -> str:
            """Compara precios del producto en multiples tiendas dentro del presupuesto."""
            return _call_tool("price_compare", product_name=product_name, max_price_usd=max_price_usd)

        @tool
        def fetch_reviews(product_name: str, focus_audience: str = "general") -> str:
            """Obtiene resenas del producto: rating, pros y contras."""
            return _call_tool("fetch_reviews", product_name=product_name, focus_audience=focus_audience)

        @tool
        def user_memory(user_id: str, action: str, data: dict = None) -> str:
            """Lee o guarda preferencias del usuario."""
            return _call_tool("user_memory", user_id=user_id, action=action, data=data)

        _agent = Agent(
            model="us.amazon.nova-pro-v1:0",
            system_prompt="""Eres ShopMind, un asistente personal de compras experto y amigable.

Cuando el usuario pida un producto:
1. Usa web_search para encontrar productos relevantes
2. Usa price_compare para comparar precios dentro del presupuesto
3. Usa fetch_reviews para obtener ratings y reseñas
4. Usa user_memory para recordar preferencias del usuario

Combina todo en una recomendación clara en español con:
- Top 3 opciones con precio, rating y razón
- Tu recomendación final con un emoji por producto

Sé conciso y amigable. No sugieras productos que superen el presupuesto.""",
            tools=[web_search, price_compare, fetch_reviews, user_memory],
        )
    return _agent


def handler(event, context):
    if event.get("requestContext", {}).get("http", {}).get("method") == "OPTIONS":
        return {"statusCode": 200, "headers": CORS, "body": ""}

    try:
        body    = json.loads(event.get("body") or "{}")
        message = body.get("message", "")

        agent  = _get_agent()
        result = agent(message)
        msg    = result.message if hasattr(result, "message") else result
        if isinstance(msg, dict):
            content = msg.get("content", [])
            text = content[0].get("text", str(msg)) if content else str(msg)
        else:
            text = str(msg)

        return {
            "statusCode": 200,
            "headers": {**CORS, "Content-Type": "application/json"},
            "body": json.dumps({"text": text}),
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {**CORS, "Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)}),
        }
