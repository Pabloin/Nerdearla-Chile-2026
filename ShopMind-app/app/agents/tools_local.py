"""
Local tool wrappers — scrapes MercadoLibre Chile in real-time via Puppeteer.
Each scrape is persisted to app/data/scrapes/
"""
import json, os, subprocess, re
from datetime import datetime
from strands import tool

_SCRAPER_PATH = os.path.join(os.path.dirname(__file__), "scraper.js")
_SCRAPES_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "scrapes")
os.makedirs(_SCRAPES_DIR, exist_ok=True)
_user_prefs = {}


def _slugify(text: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', text.lower().strip())[:60].strip('-')


def _scrape(query: str, limit: int = 10) -> list:
    """Run Puppeteer scraper, persist results, and return product list."""
    try:
        result = subprocess.run(
            ["node", _SCRAPER_PATH, query, str(limit)],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode == 0 and result.stdout.strip():
            products = json.loads(result.stdout)
            # Persist scrape
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            slug = _slugify(query)
            filename = f"{ts}_{slug}.json"
            filepath = os.path.join(_SCRAPES_DIR, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump({"query": query, "timestamp": ts, "count": len(products), "results": products}, f, ensure_ascii=False, indent=2)
            print(f"Scrape saved: {filename} ({len(products)} products)")
            return products
    except Exception as e:
        print(f"Scraper error: {e}")
    return []


@tool
def web_search(query: str, max_results: int = 10) -> str:
    """Busca productos en MercadoLibre Chile en tiempo real. Retorna productos reales con precios y URLs."""
    products = _scrape(query, max_results)
    return json.dumps(products, ensure_ascii=False)


@tool
def price_compare(product_name: str, max_price_usd: float) -> str:
    """Busca productos dentro del presupuesto en MercadoLibre Chile."""
    products = _scrape(product_name, 15)
    filtered = [p for p in products if p.get("price_usd", 9999) <= max_price_usd]
    filtered.sort(key=lambda x: x.get("price_usd", 0))
    return json.dumps(filtered[:10], ensure_ascii=False)


@tool
def fetch_reviews(product_name: str, focus_audience: str = "general") -> str:
    """Busca productos y retorna los que tienen mejor rating."""
    products = _scrape(product_name, 10)
    with_rating = [p for p in products if p.get("rating")]
    with_rating.sort(key=lambda x: -x.get("rating", 0))
    return json.dumps(with_rating[:5], ensure_ascii=False)


@tool
def user_memory(user_id: str, action: str, data: dict = None) -> str:
    """Lee o guarda preferencias del usuario."""
    if action == "get":
        return json.dumps(_user_prefs.get(user_id, {"budget_usd": None, "preferences": [], "history": []}), ensure_ascii=False)
    else:
        _user_prefs[user_id] = data or {}
        return json.dumps({"saved": True, "user_id": user_id}, ensure_ascii=False)
