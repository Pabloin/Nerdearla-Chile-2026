"""
Test the local setup with updated system prompt
Uses local tools (no AWS credentials needed)
"""
import asyncio
import sys
sys.path.insert(0, '.')

# Patch tools to use local versions before importing the agent
import agents.tools_local as tools_local
sys.modules['agents.tools'] = tools_local

async def main():
    from agents.supervisor_agent import _get_agent

    print("🔧 Initializing agent with NEW system prompt...")
    agent = _get_agent()

    print("\n📝 Testing query: 'iphone 500 usd'\n")

    result = await agent.invoke_async("un iphone de 500 usd")

    print("="*60)
    print("RESPONSE:")
    print("="*60)
    print(result.message)
    print("="*60)

    # Check if URLs are present
    if "https://" in result.message or "http://" in result.message:
        print("\n✅ SUCCESS: URLs are included in response!")
    else:
        print("\n⚠️  WARNING: No URLs found in response")

if __name__ == "__main__":
    asyncio.run(main())
