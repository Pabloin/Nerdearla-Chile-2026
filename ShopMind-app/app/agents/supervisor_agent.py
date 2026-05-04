"""
supervisor_agent.py
ShopMind — Strands Agent that connects to MCP server for tools.
"""
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

_agent = None


def _get_agent():
    global _agent
    if _agent is None:
        from strands import Agent
        from strands.tools.mcp import MCPClient
        from mcp.client.streamable_http import streamablehttp_client

        mcp_client = MCPClient(
            lambda: streamablehttp_client("http://localhost:8001/mcp")
        )

        _agent = Agent(
            model="us.amazon.nova-pro-v1:0",
            system_prompt="""Eres ShopMind, un asistente personal de compras experto para Chile.
Tus herramientas buscan productos reales en MercadoLibre Chile en tiempo real.

Cuando el usuario pida un producto:
1. Usa web_search para buscar productos que coincidan con su consulta
2. Usa price_compare si menciona un presupuesto, para filtrar por precio
3. Usa fetch_reviews para obtener los productos mejor valorados
4. Usa user_memory para recordar preferencias del usuario

Formato de respuesta en espanol:
- Muestra los mejores productos encontrados (maximo 3-5)
- Para cada producto incluye: nombre, precio (CLP y USD), y URL de MercadoLibre
- SIEMPRE muestra la URL completa visible, ejemplo: [https://www.mercadolibre.cl/producto...](https://www.mercadolibre.cl/producto...)
- Si el usuario da presupuesto en USD, filtra por ese monto
- Si da presupuesto en CLP, convierte aproximadamente (1 USD ~ 950 CLP)

IMPORTANTE:
- Todos los URLs son reales de MercadoLibre Chile - muestralos siempre
- No inventes productos ni URLs
- Se conciso y directo
- Responde siempre en espanol""",
            tools=[mcp_client],
        )
    return _agent


@app.entrypoint
async def handle(payload: dict):
    agent        = _get_agent()
    user_message = payload.get("message", "")
    async for chunk in agent.stream_async(
        user_message,
        session_id=payload.get("session_id"),
    ):
        yield chunk


if __name__ == "__main__":
    import asyncio
    async def test():
        agent  = _get_agent()
        result = await agent.invoke_async(
            "Quiero auriculares inalambricos para estudiar. Presupuesto $80."
        )
        print(result.message)
    asyncio.run(test())
