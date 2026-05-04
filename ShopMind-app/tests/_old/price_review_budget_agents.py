"""
price_agent.py — Specialist: Price Comparison
review_agent.py — Specialist: Review Analysis
budget_agent.py — Specialist: Budget & Memory
"""
from strands import Agent
from agents.tools import price_compare, fetch_reviews, user_memory

price_agent = Agent(
    name="price_agent",
    description="Compares prices for given products across multiple stores. Returns best prices per product.",
    model="us.amazon.nova-lite-v1:0",
    system_prompt="""Eres un especialista en comparación de precios.
Dado una lista de productos, usa price_compare para encontrar el mejor precio disponible.
Devuelve SOLO JSON:
[{"product": str, "best_price_usd": float, "store": str, "url": str}]""",
    tools=[price_compare],
)

review_agent = Agent(
    name="review_agent",
    description="Analyzes user reviews for products. Returns rating, review count, and key pros/cons.",
    model="us.amazon.nova-lite-v1:0",
    system_prompt="""Eres un especialista en análisis de reseñas.
Analiza las reseñas de los productos y devuelve SOLO JSON:
[{"product": str, "rating": float, "review_count": int, "pros": [str], "cons": [str], "best_for": str}]
Enfócate en reseñas de estudiantes cuando sea relevante.""",
    tools=[fetch_reviews],
)

budget_agent = Agent(
    name="budget_agent",
    description="Checks user budget, retrieves preferences from memory, and validates product recommendations fit within budget.",
    model="us.amazon.nova-lite-v1:0",
    system_prompt="""Eres un especialista en presupuesto y preferencias de usuario.
1. Recupera las preferencias del usuario con user_memory
2. Verifica que los productos recomendados estén dentro del presupuesto
3. Guarda el presupuesto y preferencias actuales para la próxima sesión
4. Devuelve SOLO JSON:
{"budget_usd": float, "valid_products": [str], "memory_updated": bool, "note": str}""",
    tools=[user_memory],
)
