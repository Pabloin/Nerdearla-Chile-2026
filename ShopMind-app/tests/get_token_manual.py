#!/usr/bin/env python3
"""
Generate Mercado Libre Access Token - Manual Flow
User copies the authorization code manually
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def exchange_code_for_token(code, client_id, client_secret, redirect_uri):
    """Exchange authorization code for access token"""
    
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
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error exchanging code for token: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return None

def main():
    print("🛒 Mercado Libre OAuth Token Generator (Manual)")
    print("="*70)
    
    client_id = os.getenv("MERCADOLIBRE_CLIENT_ID")
    client_secret = os.getenv("MERCADOLIBRE_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("❌ Error: Missing credentials in .env file")
        print("\nMake sure you have:")
        print("MERCADOLIBRE_CLIENT_ID=your-client-id")
        print("MERCADOLIBRE_CLIENT_SECRET=your-client-secret")
        return
    
    print(f"📝 Client ID: {client_id}")
    
    # Use the redirect URI from the app settings (must match exactly what's in ML app)
    redirect_uri = "https://abc123.execute-api.us-east-1.amazonaws.com/prod/callback"
    
    print("\n⚠️  Make sure this redirect URI matches EXACTLY what's in your ML app:")
    print(f"   {redirect_uri}")
    
    # Build authorization URL
    auth_url = (
        f"https://auth.mercadolibre.com.ar/authorization"
        f"?response_type=code"
        f"&client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
    )
    
    print("\n" + "="*70)
    print("STEP 1: Get Authorization Code")
    print("="*70)
    print("\n1. Copy this URL and open it in your browser:\n")
    print(f"{auth_url}\n")
    print("2. Login with your Mercado Libre account")
    print("3. Authorize the application")
    print("4. You'll be redirected to a URL that looks like:")
    print(f"   {redirect_uri}?code=TG-XXXXXXXXX")
    print("\n5. Copy the 'code' parameter from the URL")
    print("   (everything after 'code=' and before any '&')")
    
    print("\n" + "="*70)
    
    # Get the code from user
    code = input("\nPaste the authorization code here: ").strip()
    
    if not code:
        print("❌ No code provided. Exiting.")
        return
    
    print(f"\n✅ Code received: {code[:20]}...")
    print("\n🔄 Exchanging code for access token...")
    
    token_data = exchange_code_for_token(code, client_id, client_secret, redirect_uri)
    
    if token_data:
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        expires_in = token_data.get("expires_in")
        user_id = token_data.get("user_id")
        
        print("\n" + "="*70)
        print("✅ SUCCESS! Access Token Generated")
        print("="*70)
        print(f"\nAccess Token: {access_token}")
        print(f"Refresh Token: {refresh_token}")
        print(f"Expires in: {expires_in} seconds ({expires_in/3600:.1f} hours)")
        print(f"User ID: {user_id}")
        
        print("\n📋 Add these to your .env file:")
        print(f"\nMERCADOLIBRE_ACCESS_TOKEN={access_token}")
        print(f"MERCADOLIBRE_REFRESH_TOKEN={refresh_token}")
        print(f"MERCADOLIBRE_USER_ID={user_id}")
        
        print("\n⚠️  Important:")
        print("  • Access token expires in 6 hours")
        print("  • Save the refresh token to get new access tokens")
        print("  • Refresh token is single-use only")
        
        # Optionally update .env file
        print("\n" + "="*70)
        update = input("\nDo you want to automatically update your .env file? (y/n): ").strip().lower()
        
        if update == 'y':
            try:
                # Read current .env
                with open('.env', 'r') as f:
                    lines = f.readlines()
                
                # Update or add tokens
                updated = False
                for i, line in enumerate(lines):
                    if line.startswith('MERCADOLIBRE_ACCESS_TOKEN='):
                        lines[i] = f'MERCADOLIBRE_ACCESS_TOKEN={access_token}\n'
                        updated = True
                    elif line.startswith('MERCADOLIBRE_REFRESH_TOKEN='):
                        lines[i] = f'MERCADOLIBRE_REFRESH_TOKEN={refresh_token}\n'
                    elif line.startswith('MERCADOLIBRE_USER_ID='):
                        lines[i] = f'MERCADOLIBRE_USER_ID={user_id}\n'
                
                # If not found, add them
                if not updated:
                    if not lines[-1].endswith('\n'):
                        lines.append('\n')
                    lines.append(f'MERCADOLIBRE_ACCESS_TOKEN={access_token}\n')
                    lines.append(f'MERCADOLIBRE_REFRESH_TOKEN={refresh_token}\n')
                    lines.append(f'MERCADOLIBRE_USER_ID={user_id}\n')
                
                # Write back
                with open('.env', 'w') as f:
                    f.writelines(lines)
                
                print("✅ .env file updated successfully!")
                
            except Exception as e:
                print(f"❌ Error updating .env file: {e}")
                print("Please update it manually.")
    else:
        print("\n❌ Failed to get access token")
        print("\nPossible issues:")
        print("  • The authorization code may have expired (they expire quickly)")
        print("  • The redirect_uri doesn't match your app settings")
        print("  • Invalid client credentials")
        print("\nTry running the script again and paste the code immediately after authorization.")

if __name__ == "__main__":
    main()
