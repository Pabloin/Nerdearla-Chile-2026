import os
import requests
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("MERCADOLIBRE_CLIENT_ID")
client_secret = os.getenv("MERCADOLIBRE_CLIENT_SECRET")
code = "TG-69d54ad8828c5700018e7aeb-3318835937"
redirect_uri = "http://localhost:44304/oauth/callback"

url = "https://api.mercadolibre.com/oauth/token"

payload = {
    "grant_type": "authorization_code",
    "client_id": client_id,
    "client_secret": client_secret,
    "code": code,
    "redirect_uri": redirect_uri
}

try:
    response = requests.post(url, data=payload)
    response.raise_for_status()
    
    data = response.json()
    print("\n✅ SUCCESS! Access Token Generated")
    print("="*70)
    print(f"\nAccess Token: {data.get('access_token')}")
    print(f"Refresh Token: {data.get('refresh_token')}")
    print(f"Expires in: {data.get('expires_in')} seconds")
    print(f"User ID: {data.get('user_id')}")
    
    print("\n📋 Add these to your .env file:")
    print(f"\nMERCADOLIBRE_ACCESS_TOKEN={data.get('access_token')}")
    print(f"MERCADOLIBRE_REFRESH_TOKEN={data.get('refresh_token')}")
    print(f"MERCADOLIBRE_USER_ID={data.get('user_id')}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Response: {e.response.text}")
