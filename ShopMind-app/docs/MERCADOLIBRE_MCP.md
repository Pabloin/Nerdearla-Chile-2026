# Mercado Libre MCP Server Integration

## Overview

This project now integrates with [Mercado Libre's official MCP Server](https://global-selling.mercadolibre.com/devsite/campaigns-ads-and-metrics/mcp-server-from-mercado-libre), enabling AI-powered interactions with Mercado Libre's APIs and documentation.

## Setup

### 1. Get Your Credentials

You've already created a developer app in Mercado Libre. You should have:
- Client ID
- Client Secret  
- Access Token

### 2. Configure Environment Variables

Create a `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
```

Add your Mercado Libre credentials:

```bash
MERCADOLIBRE_CLIENT_ID=your-client-id
MERCADOLIBRE_CLIENT_SECRET=your-client-secret
MERCADOLIBRE_ACCESS_TOKEN=your-access-token
```

### 3. Configure MCP Server in Kiro

Edit `.kiro/settings/mcp.json` and replace `YOUR_ACCESS_TOKEN_HERE` with your actual access token:

```json
{
  "mcpServers": {
    "mercadolibre": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://mcp.mercadolibre.com/mcp",
        "--header",
        "Authorization:${MERCADOLIBRE_AUTH_HEADER}"
      ],
      "env": {
        "MERCADOLIBRE_AUTH_HEADER": "Bearer YOUR_ACCESS_TOKEN_HERE"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### 4. Restart Kiro

After updating the configuration, restart Kiro to load the MCP server.

## Available Tools

The Mercado Libre MCP server provides two main tools:

### 1. `search_documentation`

Search across all Mercado Libre developer documentation.

**Parameters:**
- `query` (required): Keywords to search for
- `language` (required): Language code (e.g., `en_us`, `es_ar`, `pt_br`)
- `siteId` (optional): Country ID (e.g., `MLA`, `MLB`, `MLM`)
- `limit` (optional): Maximum number of results
- `offset` (optional): Number of results to skip

**Example:**
```
Search Mercado Libre docs for "product listing API" in Spanish for Argentina
```

### 2. `get_documentation_page`

Retrieve the full content of a specific documentation page.

**Parameters:**
- `path` (required): Path of the page to retrieve
- `language` (required): Language code (e.g., `en_us`, `es_ar`, `pt_br`)
- `siteId` (optional): Country ID (e.g., `MLA`, `MLB`, `MLM`)

**Example:**
```
Get the full OAuth authentication documentation page from Mercado Libre
```

## Testing

Run the test script to verify your setup:

```bash
python test_mercadolibre_mcp.py
```

## Integration with ShopMind

You can now enhance ShopMind to:

1. **Search real products** from Mercado Libre instead of mock data
2. **Get real prices** from Mercado Libre listings
3. **Access product reviews** from actual Mercado Libre products
4. **Query documentation** to help users integrate with Mercado Libre APIs

### Example Integration

Create a new tool in `agents/tools.py`:

```python
@tool
def search_mercadolibre_products(query: str, max_price: float = None) -> str:
    """
    Search for products on Mercado Libre
    
    Args:
        query: Product search query
        max_price: Maximum price filter (optional)
    
    Returns:
        JSON string with product results
    """
    # Use Mercado Libre API via MCP tools
    # Implementation here
    pass
```

## Troubleshooting

### Token Issues

If you see "Loading Tools" indefinitely or connection failures:

1. Verify your access token is valid and not expired
2. Check the token format in `.kiro/settings/mcp.json`
3. Ensure there are no extra spaces or missing characters
4. Generate a new access token if needed

### MCP Server Not Appearing

1. Check the configuration in `.kiro/settings/mcp.json`
2. Restart Kiro
3. Look for MCP-related errors in Kiro's output panel

## Resources

- [Mercado Libre MCP Server Documentation](https://global-selling.mercadolibre.com/devsite/campaigns-ads-and-metrics/mcp-server-from-mercado-libre)
- [Mercado Libre Developer Portal](https://developers.mercadolibre.com/)
- [Model Context Protocol Specification](https://github.com/modelcontextprotocol)
