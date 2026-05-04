"""
backend_local.py — ShopMind local backend
Connects to the MCP server for tools, runs Strands agent with Nova.
Usage:
  Terminal 1: python3 mcp_server.py          (MCP tools)
  Terminal 2: AWS_PROFILE=bedrock_nova python3 backend_local.py  (agent + API)
  Terminal 3: cd frontend && npm run dev     (UI)
"""
import json, uuid, re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_agent = None


def get_agent():
    global _agent
    if _agent is None:
        from agents.supervisor_agent import _get_agent
        _agent = _get_agent()
    return _agent


class InvokeRequest(BaseModel):
    message: str
    user_id: str = "nerdearla-demo"
    session_id: str = None


@app.post("/invoke")
async def invoke(req: InvokeRequest):
    session_id = req.session_id or str(uuid.uuid4())
    agent = get_agent()

    try:
        result = await agent.invoke_async(req.message, session_id=session_id)

        text = ""
        if hasattr(result, 'message'):
            msg = result.message
            if isinstance(msg, dict) and 'content' in msg:
                content = msg['content']
                if isinstance(content, list) and len(content) > 0:
                    text = content[0].get('text', '')
            elif isinstance(msg, str):
                text = msg
            else:
                text = str(msg)
        elif isinstance(result, dict):
            if 'content' in result:
                content = result['content']
                if isinstance(content, list) and len(content) > 0:
                    text = content[0].get('text', str(result))
                else:
                    text = str(content)
            else:
                text = str(result)
        else:
            text = str(result)

        text = re.sub(r'<thinking>.*?</thinking>', '', text, flags=re.DOTALL).strip()

        # Extract tool results from the CURRENT turn only.
        # Find the last plain user message (the current query) and scan forward from there.
        tool_results = {}
        if hasattr(agent, 'messages'):
            messages = agent.messages
            # Walk backward to find the last user message that is plain text (not tool results)
            start_idx = 0
            for i in range(len(messages) - 1, -1, -1):
                msg = messages[i]
                if msg.get('role') == 'user':
                    content = msg.get('content', [])
                    has_tool_result = any(
                        isinstance(b, dict) and 'toolResult' in b
                        for b in (content if isinstance(content, list) else [])
                    )
                    if not has_tool_result:
                        start_idx = i
                        break

            # Scan forward from the current query to collect tool calls and results
            tool_use_map = {}  # toolUseId -> tool_name
            for msg in messages[start_idx:]:
                if msg.get('role') == 'assistant':
                    for block in msg.get('content', []):
                        if isinstance(block, dict) and 'toolUse' in block:
                            tool_name = block['toolUse'].get('name', '')
                            tool_input = block['toolUse'].get('input', {})
                            tool_use_id = block['toolUse'].get('toolUseId', '')
                            tool_use_map[tool_use_id] = tool_name
                            tool_results[tool_name] = {"input": tool_input}
                if msg.get('role') == 'user':
                    for block in msg.get('content', []):
                        if isinstance(block, dict) and 'toolResult' in block:
                            tool_use_id = block['toolResult'].get('toolUseId', '')
                            result_content = block['toolResult'].get('content', [])
                            result_text = result_content[0].get('text', '') if result_content else ''
                            tool_name = tool_use_map.get(tool_use_id)
                            if tool_name and tool_name in tool_results:
                                try:
                                    tool_results[tool_name]['output'] = json.loads(result_text)
                                except (json.JSONDecodeError, TypeError):
                                    tool_results[tool_name]['output'] = result_text

        return {"text": text, "tool_results": tool_results}

    except Exception as e:
        import traceback
        print(f"Backend error: {traceback.format_exc()}")
        return {"text": f"Error: {str(e)}", "error": True, "tool_results": {}}


@app.get("/health")
def health():
    return {"status": "ok", "mode": "local"}


if __name__ == "__main__":
    import uvicorn
    print("ShopMind backend starting on http://localhost:8000")
    print("Make sure MCP server is running on :8001")
    uvicorn.run(app, host="0.0.0.0", port=8000)
