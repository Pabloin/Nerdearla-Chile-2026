"""search_agent.py — Specialist: Product Search"""
from strands import Agent
from agents.tools import web_search

search_agent = Agent(
    name="search_agent",
    description="Searches for products matching the user's requirements. Returns product names, models, and basic specs.",
    model="us.amazon.nova-lite-v1:0",
    system_prompt="""Eres un especialista en búsqueda de productos.
Dado un query de producto, busca en la web y devuelve los 5 productos más relevantes
con: nombre, modelo, precio aproximado y especificaciones clave.
Responde SOLO con JSON. Formato:
[{"name": str, "model": str, "price_usd": float, "specs": [str]}]""",
    tools=[web_search],
)
