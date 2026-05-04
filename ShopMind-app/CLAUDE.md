# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ShopMind is a demonstration e-commerce personal shopping assistant built for Nerdearla Chile 2025. It showcases Amazon Bedrock AgentCore with MCP (Model Context Protocol) tools, featuring a supervisor agent that orchestrates multiple specialized tools to help users find products within budget constraints.

**Key Technologies:**
- Amazon Bedrock AgentCore (agent orchestration)
- Strands Agents framework (agent implementation)
- FastMCP (MCP server implementation)
- React + Vite (frontend)
- FastAPI (backend proxy)
- AWS Lambda (tool backends)

## Development Modes

### Local Development (Recommended for Testing)
Runs the agent directly without AgentCore cold start delays:

```bash
# Activate the virtual environment (already created at .venv)
source .venv/bin/activate

# Backend (runs agent locally)
python3 backend_local.py

# Frontend (in a second terminal)
cd frontend && npm run dev
```

> **Note**: Use `python3` not `python` on macOS. The `.venv` folder is hidden — use `ls -la` to see it.

The local backend (`backend_local.py`) imports and runs the supervisor agent directly, avoiding AgentCore runtime overhead. Use this for rapid iteration.

### Production Mode (AWS AgentCore)
Deploys to AWS AgentCore Runtime with full observability:

```bash
# Deploy everything
cd infra && bash deploy.sh

# Or deploy individually
agentcore deploy  # uses .bedrock_agentcore.yaml config

# Backend proxy (connects to deployed agent)
python backend.py
```

The production backend (`backend.py`) calls the deployed AgentCore runtime via boto3.

## Architecture

### Agent Flow
```
User → Backend → Supervisor Agent → Tools → Lambda (shopmind-tools)
                                   ↓
                           MCP Servers (optional, for AgentCore Gateway demo)
```

**Supervisor Agent** (`agents/supervisor_agent.py`):
- Single agent with 4 tools: `web_search`, `price_compare`, `fetch_reviews`, `user_memory`
- Uses Strands framework with Amazon Nova Pro model (`us.amazon.nova-pro-v1:0`)
- System prompt optimized for Spanish e-commerce recommendations
- Designed for fast cold start (< 30s AgentCore init limit)

**Tools** (`agents/tools.py`):
- Direct Lambda invocation (no MCP, no gateway, no token expiry issues)
- All tools call the `shopmind-tools` Lambda function
- Strands `@tool` decorators for agent integration

**MCP Servers** (`mcp_servers/`):
- Alternative implementation for AgentCore Gateway demo
- `mcp_search_review_servers.py`: web_search + fetch_reviews
- `mcp_price_server.py`: price_compare + user_memory
- Only used when deploying with AgentCore Gateway setup

### Key Design Decisions

1. **Simplified Architecture**: Originally designed with 4 separate agents (search, price, reviews, budget), now consolidated to a single supervisor agent with tools for faster cold start and simpler deployment.

2. **Direct Lambda Calls**: Tools bypass the MCP Gateway and call Lambda directly to avoid:
   - Cognito token expiry during development
   - Gateway target sync delays
   - Additional network hops

3. **Two Backend Options**:
   - `backend_local.py` for development (no cold start)
   - `backend.py` for production demos (full observability)

## AWS Configuration

**Profile**: Use `chile` profile for all AWS operations
**Region**: `us-east-1`
**Account**: `703671890483`

Key environment variables (see `.env.example` or `MEMORY.md`):
- `AWS_PROFILE=chile`
- `AWS_DEFAULT_REGION=us-east-1`

## Common Commands

### Testing Locally
```bash
# Activate venv first
source .venv/bin/activate

# Quick agent test
python3 test_local.py

# Full local stack
python3 backend_local.py  # Terminal 1
cd frontend && npm run dev  # Terminal 2
```

### Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Deploy to AWS
cd infra && bash deploy.sh

# Individual component deployment
agentcore deploy  # deploys all agents in .bedrock_agentcore.yaml
```

### Frontend
```bash
cd frontend
npm install
npm run dev      # development server
npm run build    # production build
npm run preview  # preview production build
```

## Critical Implementation Notes

### AgentCore Configuration (`.bedrock_agentcore.yaml`)
- Three agents defined: `shopmind_mcp_search_review`, `shopmind_mcp_price`, `shopmind_supervisor`
- MCP agents use `protocol: MCP`, supervisor uses `protocol: HTTP`
- All use `deployment_type: direct_code_deploy` with `runtime_type: PYTHON_3_12`
- Platform: `linux/arm64` for cost optimization

### Dependencies (requirements.txt)
- **CRITICAL**: Use `bedrock-agentcore>=1.4.0` (NOT `amazon-bedrock-agentcore`)
- `strands-agents>=0.1.0` for agent framework
- `mcp>=1.0.0` for MCP protocol
- FastAPI/uvicorn for backends

### AgentCore CLI Usage
- Use `agentcore deploy` (NOT `agentcore launch`)
- Gateway mcpServer targets require OAUTH — cannot point directly at AgentCore runtimes

### Streaming Responses
Both backends implement Server-Sent Events (SSE) streaming:
- Format: `data: {"text": "..."}\n\n`
- Completion: `data: [DONE]\n\n`
- Strands agents send full text with each chunk (not incremental)

### Cognito Authentication (Gateway Setup)
When setting up AgentCore Gateway (`infra/setup_gateway.py`):
- Requires valid Cognito client credentials
- Tokens expire — regenerate before redeployment
- Discovery URL format: `https://<domain>.auth.<region>.amazoncognito.com/.well-known/openid-configuration`

## Frontend Configuration

The frontend (`frontend/.env`) needs:
```
VITE_AGENT_ARN=<supervisor agent ARN>
VITE_REGION=us-east-1
VITE_AGENT_URL=<backend URL>
```

Backend URL defaults:
- Local dev: `http://localhost:8000`
- Production: Lambda Function URL or API Gateway endpoint

## Project Structure Context

- `agents/supervisor_agent.py` — Main agent entrypoint (BedrockAgentCoreApp)
- `agents/tools.py` — Strands tool wrappers for Lambda calls
- `mcp_servers/` — Alternative MCP implementations (optional)
- `backend.py` / `backend_local.py` — FastAPI proxies (production/dev)
- `infra/setup_gateway.py` — AgentCore Gateway + Cognito setup
- `infra/deploy.sh` — One-command full deployment script
- `.bedrock_agentcore.yaml` — AgentCore deployment configuration

## Testing Strategy

1. **Local agent testing**: `python3 test_local.py`
2. **Local full stack**: Run `python3 backend_local.py` + frontend dev server
3. **Production validation**: Deploy to AgentCore, test via `backend.py`
4. **Lambda testing**: Invoke `shopmind-tools` Lambda directly with test payloads

The local backend is preferred for development as it eliminates cold start delays and provides immediate feedback on agent behavior changes.
