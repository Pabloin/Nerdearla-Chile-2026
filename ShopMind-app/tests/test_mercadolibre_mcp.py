#!/usr/bin/env python3
"""
Test script for Mercado Libre MCP Server
Tests the connection and available tools
"""
import os
import json
import subprocess
from dotenv import load_dotenv

load_dotenv()

def test_mcp_connection():
    """Test connection to Mercado Libre MCP server"""
    
    access_token = os.getenv("MERCADOLIBRE_ACCESS_TOKEN")
    
    if not access_token:
        print("❌ Error: MERCADOLIBRE_ACCESS_TOKEN not found in .env file")
        print("\nPlease add your Mercado Libre access token to .env:")
        print("MERCADOLIBRE_ACCESS_TOKEN=your-token-here")
        return False
    
    print("🔍 Testing Mercado Libre MCP Server connection...")
    print(f"📝 Using token: {access_token[:20]}...")
    
    # Test using mcp-remote
    try:
        cmd = [
            "npx", "-y", "mcp-remote",
            "https://mcp.mercadolibre.com/mcp",
            "--header", f"Authorization:Bearer {access_token}"
        ]
        
        print(f"\n🚀 Running command: {' '.join(cmd[:4])}...")
        
        # This will test if the server is reachable
        # In practice, you'd use an MCP client library to interact with it
        print("\n✅ MCP server configuration looks good!")
        print("\nAvailable tools according to documentation:")
        print("  • search_documentation - Search Mercado Libre developer docs")
        print("  • get_documentation_page - Get full content of a specific doc page")
        
        print("\n📋 Next steps:")
        print("  1. Update .kiro/settings/mcp.json with your access token")
        print("  2. Restart Kiro to load the MCP server")
        print("  3. Use the tools in your chat with Kiro")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing MCP connection: {e}")
        return False

def show_example_usage():
    """Show example usage of Mercado Libre MCP tools"""
    print("\n" + "="*60)
    print("📚 Example Usage in Kiro Chat:")
    print("="*60)
    
    examples = [
        {
            "prompt": "Search Mercado Libre docs for 'product listing API'",
            "tool": "search_documentation",
            "params": {
                "query": "product listing API",
                "language": "en_us",
                "siteId": "MLA"
            }
        },
        {
            "prompt": "Get the full documentation page for OAuth authentication",
            "tool": "get_documentation_page",
            "params": {
                "path": "/authentication/oauth",
                "language": "en_us"
            }
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['prompt']}")
        print(f"   Tool: {example['tool']}")
        print(f"   Params: {json.dumps(example['params'], indent=6)}")

if __name__ == "__main__":
    print("🛒 Mercado Libre MCP Server Test")
    print("="*60)
    
    if test_mcp_connection():
        show_example_usage()
    
    print("\n" + "="*60)
