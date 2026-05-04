#!/usr/bin/env python3
"""
Generate Mercado Libre Access Token using OAuth Authorization Code Flow.
Uses the existing registered redirect URI — you paste the code manually.
"""
import os
import requests
from dotenv import load_dotenv
import webbrowser

load_dotenv()

REDIRECT_URI = "https://abc123.execute-api.us-east-1.amazonaws.com/prod/callback"


def exchange_code_for_token(code, client_id, client_secret):
    """Exchange authorization code for access token"""
    resp = requests.post("https://api.mercadolibre.com/oauth/token", data={
        "grant_type": "authorization_code",
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "redirect_uri": REDIRECT_URI,
    })
    resp.raise_for_status()
    return resp.json()


def main():
    print("Mercado Libre OAuth Token Generator")
    print("=" * 70)

    client_id = os.getenv("MERCADOLIBRE_CLIENT_ID")
    client_secret = os.getenv("MERCADOLIBRE_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("Error: Missing MERCADOLIBRE_CLIENT_ID or MERCADOLIBRE_CLIENT_SECRET in .env")
        return

    auth_url = (
        f"https://auth.mercadolibre.com.ar/authorization"
        f"?response_type=code"
        f"&client_id={client_id}"
        f"&redirect_uri={REDIRECT_URI}"
    )

    print(f"\nOpening browser...\n")
    print(f"If it doesn't open, visit:\n{auth_url}\n")
    webbrowser.open(auth_url)

    print("After authorizing, the browser will redirect to a dead page.")
    print("Copy the 'code' parameter from the URL bar.")
    print("Example: ...callback?code=TG-xxxx-xxxx")
    print()
    code = input("Paste the code here: ").strip()

    if not code:
        print("No code provided.")
        return

    print("\nExchanging code for access token...")
    try:
        data = exchange_code_for_token(code, client_id, client_secret)
    except Exception as e:
        print(f"Error: {e}")
        return

    print("# ======================================================================")
    print("# SUCCESS — Add these to your .env file:")
    print("# ======================================================================")
    print(f"\nMERCADOLIBRE_ACCESS_TOKEN={data['access_token']}")
    print(f"MERCADOLIBRE_REFRESH_TOKEN={data.get('refresh_token', '')}")
    print(f"MERCADOLIBRE_USER_ID={data.get('user_id', '')}")
    print(f"\nExpires in: {data.get('expires_in', 0) / 3600:.1f} hours")


if __name__ == "__main__":
    main()
