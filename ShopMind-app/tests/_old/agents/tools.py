"""
Direct Lambda tool wrappers — no MCPClient, no gateway, no token expiry.
Each function calls shopmind-tools Lambda directly.
"""
import boto3, json
from strands import tool

_lambda = boto3.client("lambda", region_name="us-east-1")
TOOLS_LAMBDA = "shopmind-tools"


def _call(tool_name: str, **kwargs) -> str:
    resp = _lambda.invoke(
        FunctionName=TOOLS_LAMBDA,
        Payload=json.dumps({"tool": tool_name, **kwargs}),
    )
    result = json.loads(resp["Payload"].read())
    return json.dumps(result, ensure_ascii=False)


@tool
def web_search(query: str, max_results: int = 10) -> str:
    """Busca productos en la web. Retorna lista de resultados con titulo y URL."""
    return _call("web_search", query=query, max_results=max_results)


@tool
def price_compare(product_name: str, max_price_usd: float) -> str:
    """Compara precios del producto en multiples tiendas dentro del presupuesto."""
    return _call("price_compare", product_name=product_name, max_price_usd=max_price_usd)


@tool
def fetch_reviews(product_name: str, focus_audience: str = "general") -> str:
    """Obtiene resenas del producto: rating, pros y contras."""
    return _call("fetch_reviews", product_name=product_name, focus_audience=focus_audience)


@tool
def user_memory(user_id: str, action: str, data: dict = None) -> str:
    """Lee o guarda preferencias del usuario."""
    return _call("user_memory", user_id=user_id, action=action, data=data)
