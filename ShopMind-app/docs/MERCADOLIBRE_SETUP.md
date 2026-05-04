# Mercado Libre OAuth Setup Guide

## Step 1: Update Redirect URI in Your App

1. Go to your Mercado Libre app settings (where you saw the configuration screenshot)
2. Find "Redirect URIs" section
3. Add this URL: `http://localhost:8080/callback`
4. Click "Agregar Redirect URI" or "Add Redirect URI"
5. Save the changes

## Step 2: Generate Access Token

Run the token generator script:

```bash
source .venv/bin/activate
python get_mercadolibre_token.py
```

This will:
1. Open your browser automatically
2. Ask you to login with your Mercado Libre account
3. Request authorization for your app
4. Receive the authorization code
5. Exchange it for an access token
6. Display the token for you to copy

## Step 3: Update .env File

Copy the access token and refresh token from the script output and add them to your `.env` file:

```bash
MERCADOLIBRE_ACCESS_TOKEN=APP_USR-xxxxx-xxxxxx-xxxxx
MERCADOLIBRE_REFRESH_TOKEN=TG-xxxxx-xxxxx
MERCADOLIBRE_USER_ID=123456789
```

## Step 4: Update MCP Configuration

Edit `.kiro/settings/mcp.json` and replace `YOUR_ACCESS_TOKEN_HERE` with your actual access token.

## Step 5: Test the Connection

```bash
python test_mercadolibre_mcp.py
```

## Important Notes

- Access tokens expire in 6 hours
- Refresh tokens are single-use only
- Save the refresh token to get new access tokens without re-authorizing
- The redirect URI must match exactly what's configured in your app

## Troubleshooting

### "Redirect URI mismatch" error
Make sure `http://localhost:8080/callback` is added to your app's redirect URIs.

### Browser doesn't open
Copy the URL from the terminal and paste it in your browser manually.

### "Invalid grant" error
The authorization code may have expired. Run the script again.

## Next Steps

Once you have the access token:
1. Test the MCP server connection
2. Restart Kiro to load the MCP server
3. Start using Mercado Libre tools in your ShopMind agent
