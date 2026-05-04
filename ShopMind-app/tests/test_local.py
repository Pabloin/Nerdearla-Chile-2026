"""Quick local test of the supervisor agent"""
import asyncio
import sys
sys.path.insert(0, '.')

async def main():
    from agents.supervisor_agent import _get_agent
    
    print("Initializing agent...")
    agent = _get_agent()
    
    print("Sending test message...")
    result = await agent.invoke_async("Hola, ¿puedes ayudarme?")
    print(f"\nResponse: {result.message}")

if __name__ == "__main__":
    asyncio.run(main())
