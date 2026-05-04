"""
setup_gateway.py
Creates the AgentCore Gateway and registers deployed MCP servers as targets.
Run once after deploying the MCP servers.
"""

import boto3, json, time, os
from urllib.parse import quote

session = boto3.Session(profile_name=os.environ.get("AWS_PROFILE", "chile"), region_name="us-east-1")
client = session.client("bedrock-agentcore-control")

TAGS = {
    "Project":      "ShopMind",
    "ProjectOwner": "Pablo Ezequiel Inchausti",
    "ProjectEvent": "Nerdearla Chile AWS Booth",
}

COGNITO_CLIENT_ID    = os.environ["COGNITO_CLIENT_ID"]
COGNITO_DISCOVERY_URL = os.environ["COGNITO_DISCOVERY_URL"]

# AgentCore runtime IDs (from agentcore deploy output)
AGENT_RUNTIME_IDS = {
    "SearchReview": os.environ["SEARCH_REVIEW_RUNTIME_ID"],
    "Price":        os.environ["PRICE_RUNTIME_ID"],
}

REGION       = "us-east-1"
ACCOUNT      = "703671890483"
GATEWAY_ROLE = f"arn:aws:iam::{ACCOUNT}:role/ShopMindGatewayRole"
DP_BASE      = f"https://bedrock-agentcore.{REGION}.amazonaws.com"


def runtime_endpoint(runtime_id: str) -> str:
    """Construct the HTTP invocation endpoint URL for an AgentCore runtime."""
    arn = f"arn:aws:bedrock-agentcore:{REGION}:{ACCOUNT}:runtime/{runtime_id}"
    return f"{DP_BASE}/runtimes/{quote(arn, safe='')}/invocations"


def create_gateway() -> str:
    print("Creating AgentCore Gateway...")
    response = client.create_gateway(
        name="shopmind-gateway",
        protocolType="MCP",
        roleArn=GATEWAY_ROLE,
        authorizerType="CUSTOM_JWT",
        authorizerConfiguration={
            "customJWTAuthorizer": {
                "allowedClients": [COGNITO_CLIENT_ID],
                "discoveryUrl":   COGNITO_DISCOVERY_URL,
            }
        },
        tags=TAGS,
    )
    gateway_id = response["gatewayId"]
    print(f"Gateway created: {gateway_id}")
    return gateway_id


def register_targets(gateway_id: str):
    target_ids = []
    for name, runtime_id in AGENT_RUNTIME_IDS.items():
        endpoint = runtime_endpoint(runtime_id)
        print(f"Registering target '{name}' -> {endpoint}")
        resp = client.create_gateway_target(
            gatewayIdentifier=gateway_id,
            name=f"Shopmind{name}",
            targetConfiguration={
                "mcp": {
                    "mcpServer": {
                        "endpoint": endpoint,
                    }
                }
            },
        )
        target_ids.append(resp["targetId"])
        print(f"  '{name}' registered (targetId: {resp['targetId']})")
        time.sleep(1)

    if target_ids:
        print(f"Syncing {len(target_ids)} targets...")
        client.synchronize_gateway_targets(
            gatewayIdentifier=gateway_id,
            targetIdList=target_ids,
        )
        print("  Sync requested")


def main():
    gateway_id = create_gateway()
    register_targets(gateway_id)

    gw = client.get_gateway(gatewayIdentifier=gateway_id)
    gateway_url = gw.get("gatewayUrl", "")
    print(f"\nGateway ready!")
    print(f"  AGENTCORE_GATEWAY_URL={gateway_url}")
    return gateway_url


if __name__ == "__main__":
    main()
