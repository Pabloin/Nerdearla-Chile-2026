"""
shopmind-tools Lambda
Handles: web_search, price_compare, fetch_reviews, user_memory
Called by AgentCore Gateway as MCP tool backend.
"""
import json, urllib.request, urllib.parse

# Simple in-memory "memory" (resets per cold start — fine for demo)
_memory = {}


def web_search(query: str, max_results: int = 10) -> list:
    try:
        params = urllib.parse.urlencode({"q": query, "format": "json", "no_html": 1, "no_redirect": 1})
        url = f"https://api.duckduckgo.com/?{params}"
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read())
        results = []
        for item in data.get("RelatedTopics", [])[:max_results]:
            if "Text" in item:
                results.append({"title": item["Text"][:120], "url": item.get("FirstURL", "")})
        # If no results, return search URLs
        if not results:
            query_encoded = urllib.parse.quote(query)
            results = [
                {"title": f"Buscar {query} en Amazon", "url": f"https://amazon.com/s?k={query_encoded}"},
                {"title": f"Buscar {query} en MercadoLibre", "url": f"https://mercadolibre.com/jm/search?as_word={query_encoded}"},
                {"title": f"Buscar {query} en Walmart", "url": f"https://walmart.com/search?q={query_encoded}"},
            ]
        return results
    except Exception:
        return [{"title": f"Search result for: {query}", "url": "https://google.com/search?q=" + urllib.parse.quote(query)}]


def price_compare(product_name: str, max_price_usd: float) -> list:
    import random, hashlib
    seed = int(hashlib.md5(product_name.encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)
    base = min(max_price_usd * 0.85, max_price_usd)

    # Generate fake but realistic product IDs
    product_id_base = hashlib.md5(product_name.encode()).hexdigest()[:8].upper()

    # Store configurations with PRODUCT PAGE URL patterns (not search)
    stores = [
        ("Amazon", 0.92, f"https://amazon.com/dp/B0{product_id_base[:8]}"),
        ("Best Buy", 0.88, f"https://bestbuy.com/site/{product_name.replace(' ', '-')}/{product_id_base[:8]}"),
        ("Walmart", 0.82, f"https://walmart.com/ip/{product_name.replace(' ', '-')}/{product_id_base[:9]}"),
        ("MercadoLibre", 0.79, f"https://articulo.mercadolibre.com.mx/MLM-{product_id_base[:9]}-{product_name.replace(' ', '-')}"),
        ("Falabella", 0.85, f"https://falabella.com/falabella-cl/product/{product_id_base[:8]}/{product_name.replace(' ', '-')}"),
    ]
    results = []
    for store, factor, url_pattern in stores:
        price = round(base * factor * (1 + rng.uniform(-0.05, 0.05)), 2)
        if price <= max_price_usd:
            results.append({
                "product": product_name,
                "store": store,
                "price_usd": price,
                "url": url_pattern
            })
    return sorted(results, key=lambda x: x["price_usd"])[:3]


def fetch_reviews(product_name: str, focus_audience: str = "general") -> dict:
    import hashlib
    seed = int(hashlib.md5(product_name.encode()).hexdigest()[:8], 16)
    ratings = [4.1, 4.3, 4.5, 4.6, 4.7, 4.8]
    rating = ratings[seed % len(ratings)]
    review_count = 800 + (seed % 2000)
    audience_note = f"Muy valorado por {focus_audience}" if focus_audience != "general" else "Bien valorado en general"
    return {
        "product": product_name,
        "rating": rating,
        "review_count": review_count,
        "pros": ["Buena relación precio/calidad", "Durabilidad comprobada", "Fácil de usar"],
        "cons": ["Envío puede demorar", "Garantía limitada"],
        "best_for": audience_note,
    }


def user_memory(user_id: str, action: str, data: dict = None) -> dict:
    if action == "get":
        return _memory.get(user_id, {"budget_usd": None, "preferences": [], "history": []})
    else:
        _memory[user_id] = data or {}
        return {"saved": True, "user_id": user_id}


TOOLS = {
    "web_search":     web_search,
    "price_compare":  price_compare,
    "fetch_reviews":  fetch_reviews,
    "user_memory":    user_memory,
}


def handler(event, context):
    tool_name = event.get("tool") or event.get("name") or event.get("function")
    inputs = event.get("input") or event.get("parameters") or event.get("arguments") or event
    # Remove meta-keys if inputs is the whole event
    if isinstance(inputs, dict):
        inputs = {k: v for k, v in inputs.items() if k not in ("tool", "name", "function")}
    fn = TOOLS.get(tool_name)
    if not fn:
        return {"error": f"Unknown tool: {tool_name}. Available: {list(TOOLS.keys())}"}
    try:
        if isinstance(inputs, dict):
            result = fn(**inputs)
        else:
            result = fn(inputs)
        return result
    except Exception as e:
        return {"error": str(e), "tool": tool_name}
