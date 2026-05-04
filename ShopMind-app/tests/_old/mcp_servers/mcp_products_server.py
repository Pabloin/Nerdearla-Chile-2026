"""
mcp_products_server.py — MCP server with product search tools.
Searches a local product catalog (data/products.json) from MercadoLibre Chile.

Run locally:
  python mcp_servers/mcp_products_server.py

Tools:
  - search_products: Search products by query and optional budget
  - get_product_reviews: Get reviews/pros/cons for a product
  - save_user_preference: Save user preference (in-memory)
  - get_user_preference: Get saved user preferences
"""
import json, os
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("shopmind-products")

# Load product catalog
_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "products.json")
with open(_DATA_PATH, "r", encoding="utf-8") as f:
    _PRODUCTS = json.load(f)

# In-memory user preferences (resets on restart — fine for demo)
_user_prefs = {}


@mcp.tool()
async def search_products(query: str, max_price_usd: float = 0, category: str = "") -> str:
    """
    Busca productos en el catalogo de MercadoLibre Chile.
    Filtra por palabras clave, presupuesto maximo en USD y categoria.
    Retorna productos con titulo, precio, URL real y rating.

    Args:
        query: Palabras clave para buscar (ej: "auriculares cancelacion ruido")
        max_price_usd: Presupuesto maximo en USD. 0 = sin limite.
        category: Filtrar por categoria: "auriculares", "celulares", "notebooks". Vacio = todas.
    """
    query_lower = query.lower()
    keywords = query_lower.split()

    results = []
    for product in _PRODUCTS:
        # Category filter
        if category and product["category"] != category.lower():
            continue

        # Budget filter
        if max_price_usd > 0 and product["price_usd"] > max_price_usd:
            continue

        # Keyword matching — product matches if any keyword is found in title, brand, or features
        searchable = (product["title"] + " " + product["brand"] + " " + " ".join(product["features"])).lower()
        score = sum(1 for kw in keywords if kw in searchable)

        if score > 0:
            results.append((score, product))

    # Sort by relevance (score), then by rating
    results.sort(key=lambda x: (-x[0], -x[1]["rating"]))

    # Return top 5
    output = []
    for _, p in results[:5]:
        output.append({
            "title": p["title"],
            "brand": p["brand"],
            "price_clp": p["price_clp"],
            "price_usd": p["price_usd"],
            "rating": p["rating"],
            "review_count": p["review_count"],
            "url": p["url"],
            "features": p["features"],
        })

    if not output:
        return json.dumps({"message": "No se encontraron productos que coincidan con tu busqueda.", "results": []}, ensure_ascii=False)

    return json.dumps({"results": output, "total": len(output)}, ensure_ascii=False)


@mcp.tool()
async def get_product_reviews(product_title: str) -> str:
    """
    Obtiene resenas, pros y contras de un producto especifico.

    Args:
        product_title: Titulo o nombre parcial del producto.
    """
    title_lower = product_title.lower()

    for product in _PRODUCTS:
        if title_lower in product["title"].lower() or product["brand"].lower() in title_lower:
            return json.dumps({
                "product": product["title"],
                "brand": product["brand"],
                "rating": product["rating"],
                "review_count": product["review_count"],
                "pros": product["pros"],
                "cons": product["cons"],
                "url": product["url"],
            }, ensure_ascii=False)

    return json.dumps({"error": f"Producto '{product_title}' no encontrado en el catalogo."}, ensure_ascii=False)


@mcp.tool()
async def save_user_preference(user_id: str, budget_usd: float = 0, preferred_brands: list[str] = None, notes: str = "") -> str:
    """
    Guarda las preferencias del usuario para futuras busquedas.

    Args:
        user_id: ID del usuario.
        budget_usd: Presupuesto maximo en USD.
        preferred_brands: Lista de marcas preferidas.
        notes: Notas adicionales del usuario.
    """
    _user_prefs[user_id] = {
        "budget_usd": budget_usd,
        "preferred_brands": preferred_brands or [],
        "notes": notes,
    }
    return json.dumps({"saved": True, "user_id": user_id}, ensure_ascii=False)


@mcp.tool()
async def get_user_preference(user_id: str) -> str:
    """
    Recupera las preferencias guardadas del usuario.

    Args:
        user_id: ID del usuario.
    """
    prefs = _user_prefs.get(user_id, {"budget_usd": 0, "preferred_brands": [], "notes": ""})
    return json.dumps(prefs, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8001)
