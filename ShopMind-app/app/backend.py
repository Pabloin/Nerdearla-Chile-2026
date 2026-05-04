"""
backend.py — ShopMind local backend proxy
Bridges the browser frontend → AgentCore supervisor agent.
Usage: python backend.py
"""
import json, uuid, asyncio
import boto3
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

AGENT_ARN    = "arn:aws:bedrock-agentcore:us-east-1:703671890483:runtime/shopmind_supervisor-tbOrpEGt4K"
REGION       = "us-east-1"
AWS_PROFILE  = "chile"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

session = boto3.Session(profile_name=AWS_PROFILE, region_name=REGION)
bedrock_rt = session.client("bedrock-agentcore")


class InvokeRequest(BaseModel):
    message: str
    user_id: str = "nerdearla-demo"
    session_id: str = None


@app.post("/invoke")
async def invoke(req: InvokeRequest):
    session_id = req.session_id or str(uuid.uuid4())

    def stream():
        try:
            response = bedrock_rt.invoke_agent_runtime(
                agentRuntimeArn=AGENT_ARN,
                qualifier="DEFAULT",
                runtimeSessionId=session_id,
                payload=json.dumps({
                    "message": req.message,
                    "user_id": req.user_id,
                    "session_id": session_id,
                }),
                contentType="application/json",
            )
            body = response.get("response") or response.get("body") or response.get("completion")
            if hasattr(body, "iter_chunks"):
                for chunk in body.iter_chunks():
                    text = chunk.decode("utf-8") if isinstance(chunk, bytes) else str(chunk)
                    if text:
                        yield f"data: {json.dumps({'text': text})}\n\n"
            elif hasattr(body, "read"):
                content = body.read()
                text = content.decode("utf-8") if isinstance(content, bytes) else str(content)
                yield f"data: {json.dumps({'text': text})}\n\n"
            else:
                yield f"data: {json.dumps({'text': str(body)})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'text': f'Error: {str(e)}'})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


@app.get("/health")
def health():
    return {"status": "ok", "agent": AGENT_ARN}


if __name__ == "__main__":
    import uvicorn
    print("ShopMind backend starting on http://localhost:8000")
    print(f"Agent: {AGENT_ARN}")
    uvicorn.run(app, host="0.0.0.0", port=8000)
