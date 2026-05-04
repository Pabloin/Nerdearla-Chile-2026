"""Fetches a fresh Cognito client_credentials token at runtime."""
import urllib.request, urllib.parse, base64, json, os


def get_gateway_token() -> str:
    client_id     = os.environ["COGNITO_CLIENT_ID"]
    client_secret = os.environ["COGNITO_CLIENT_SECRET"]
    token_url     = os.environ["COGNITO_TOKEN_URL"]
    scope         = os.environ.get("COGNITO_SCOPE", "https://shopmind.api/gateway")

    credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    data = urllib.parse.urlencode({"grant_type": "client_credentials", "scope": scope}).encode()
    req  = urllib.request.Request(
        token_url,
        data=data,
        headers={"Authorization": f"Basic {credentials}", "Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())["access_token"]
