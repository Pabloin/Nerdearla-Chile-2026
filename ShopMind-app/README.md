# ShopMind-app

ShopMind-app is a local-first demo of a shopping assistant built with Amazon Bedrock AgentCore, a FastMCP server, a FastAPI backend, and a React frontend.

This copy is intentionally clean: local virtual environments, `node_modules`, `.env`, and generated scrape artifacts are not included.

## Project layout

```text
ShopMind-app/
├── app/
│   ├── backend_local.py    # Local FastAPI backend that invokes the agent directly
│   ├── backend.py          # Proxy for deployed AgentCore runtime
│   ├── mcp_server.py       # Local MCP server exposing shopping tools
│   ├── agents/             # Supervisor agent + Puppeteer scraper
│   ├── frontend/           # React + Vite UI
│   └── requirements.txt    # Python dependencies
├── package.json            # Root Node dependency for Puppeteer
└── README.md
```

## Prerequisites

- Python 3.12 on macOS or Linux
- Node.js 18+ recommended
- An AWS profile with Bedrock access

If you do not have the `chile` AWS profile locally, replace it with whichever profile can access Bedrock.

## Setup

Create a virtual environment at the repo root and install Python dependencies:

```bash
cd /Users/pabloinchausti/Desktop/repos/Pabloin/Nerdearla-Chile-2026/ShopMind-app
python3.12 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r app/requirements.txt fastapi uvicorn pydantic
```

If `python3.12` is not available, install Python 3.12 first. This project does not install correctly on the system Python 3.9 that ships on older macOS setups.

Install the Node dependencies used by the scraper and the frontend:

```bash
cd /Users/pabloinchausti/Desktop/repos/Pabloin/Nerdearla-Chile-2026/ShopMind-app
npm install

cd /Users/pabloinchausti/Desktop/repos/Pabloin/Nerdearla-Chile-2026/ShopMind-app/app/frontend
npm install
```

## Run locally

You need 3 terminals.

### Terminal 1: MCP server

```bash
cd /Users/pabloinchausti/Desktop/repos/Pabloin/Nerdearla-Chile-2026/ShopMind-app
source .venv/bin/activate
cd app
python3 mcp_server.py
```

### Terminal 2: backend

```bash
cd /Users/pabloinchausti/Desktop/repos/Pabloin/Nerdearla-Chile-2026/ShopMind-app
source .venv/bin/activate
cd app
AWS_PROFILE=chile python3 backend_local.py
```

### Terminal 3: frontend

```bash
cd /Users/pabloinchausti/Desktop/repos/Pabloin/Nerdearla-Chile-2026/ShopMind-app/app/frontend
npm run dev
```

Open:

```text
http://localhost:5173
```

## Common issues

### `pip: command not found`

Use `python3 -m pip` instead of `pip`.

### `ModuleNotFoundError: No module named 'mcp'`

The virtual environment is either not activated or the Python dependencies were not installed.

If the install stopped at `strands-agents`, recreate the environment with Python 3.12 and run the install again.

### `No matching distribution found for strands-agents`

That usually means the virtual environment was created with an older Python version. The working source repo uses Python 3.12.

### `Cannot find module 'puppeteer'`

Run `npm install` at the repo root. The scraper loads Puppeteer from the root `node_modules`.

### Frontend starts but requests fail

Make sure both of these are running first:

- `app/mcp_server.py`
- `app/backend_local.py`

## Notes

- `backend_local.py` is the recommended development path.
- `backend.py` is for invoking a deployed AgentCore runtime.
- The comment inside `backend_local.py` mentioning `bedrock_nova` is stale; use the AWS profile that actually works in your environment.
