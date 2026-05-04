# ShopMind — Architecture

## App Flow

```
Browser (React)
    ↓ HTTP POST /invoke
Backend (FastAPI + Strands Agent + Nova Pro)
    ↓ MCP Protocol (streamable-http)
MCP Server (FastMCP + Puppeteer)
    ↓ Headless Chrome
MercadoLibre Chile (real website)
```

## 3 Processes Running

| Terminal | Process          | Port | Role                                                                                                      |
|----------|------------------|------|-----------------------------------------------------------------------------------------------------------|
| 1        | mcp_server.py    | 8001 | MCP tools — scrapes ML Chile via Puppeteer                                                                |
| 2        | backend_local.py | 8000 | Strands Agent + Nova Pro — receives user query, decides which tools to call via MCP, reasons over results |
| 3        | npm run dev      | 5173 | React UI — chat + agent panel with clickable tool results                                                 |

## What happens when a user asks "camisetas pokemon hasta 20 usd"

1. React sends POST to backend
2. Backend passes message to Strands Agent
3. Agent (Nova Pro) decides: "I should call `price_compare` with max_price_usd=20"
4. Strands calls `price_compare` on MCP server via MCP protocol
5. MCP server launches Puppeteer, opens `listado.mercadolibre.cl/camisetas-pokemon`
6. Puppeteer solves JS challenge, scrapes products, returns JSON
7. Scrape is saved to `data/scrapes/`
8. Results go back through MCP to the agent
9. Nova reads the products, picks the best ones, writes the response
10. Backend strips `<thinking>` tags, sends response + tool results to frontend
11. React renders markdown with clickable links + agent panel shows tool data

## Tech Stack

- **LLM**: Amazon Nova Pro (via Bedrock)
- **Agent framework**: Strands Agents
- **Tool protocol**: MCP (Model Context Protocol)
- **Scraper**: Puppeteer (headless Chrome)
- **Backend**: FastAPI
- **Frontend**: React + Vite
- **Data**: Real-time from MercadoLibre Chile

## Why MCP Server?

Without it, the tools are just Python functions called directly by the agent. That works, but it's tightly coupled — the tools only exist inside the agent process.

With an MCP server:

1. **The tools are independent** — they run as their own service. You can restart the agent without restarting the scraper, or vice versa.
2. **Any agent can use them** — not just your Strands agent. Any MCP-compatible client (Claude, another agent, a different framework) can connect to `localhost:8001` and use the same tools.
3. **It's what the talk is about** — you're presenting MCP at Nerdearla. If your demo doesn't actually use MCP protocol, you're just showing a regular agent with functions.
4. **It mirrors production** — in AgentCore, each MCP server runs in its own container. Your local setup with separate processes is the same pattern.

```
Without MCP server: Agent → calls Python function → done
With MCP server:    Agent → MCP protocol → MCP Server → Puppeteer → done
```

The second one is what you want to demo.

## Deployment Options

For the Nerdearla demo, running locally on your laptop is fine. The audience sees the same architecture.

### Easy Path — Local Demo (Recommended)

Run the 3 processes on your laptop (or an EC2 instance). Done in 5 minutes. This is the way to go for the talk — it shows the real MCP architecture without adding deployment complexity that isn't relevant to the MCP story.

### Production Path — AgentCore

If you wanted to deploy to AWS:

| Component | Deployment Target |
|-----------|-------------------|
| MCP Server | AgentCore Runtime container |
| Backend + Agent | Another AgentCore Runtime |
| Frontend | S3 + CloudFront |
| Puppeteer | Lambda with Chrome layer, or a container with headless Chrome |

The hard part is the scraper. Puppeteer needs a browser runtime, which doesn't fit Lambda easily. You'd need either a Lambda layer with headless Chrome or a dedicated container — neither is trivial, and neither adds to the MCP demo narrative.
