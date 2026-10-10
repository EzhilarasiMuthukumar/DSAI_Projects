"""
Smoke test for the SPIN Coach agent.
Verifies the agent can load, process a message, and call tools.

Usage:
    python scripts/test_agent.py
"""

import asyncio
import sys
from pathlib import Path

# Add agent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "agent"))


async def test_agent():
    """Run a quick test to verify agent setup."""
    try:
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService
        from google.genai import types
        from spin_coach import root_agent

        print("✅ Agent imported successfully")
        print(f"   Name: {root_agent.name}")
        print(f"   Model: {root_agent.model}")
        print(f"   Tools: {len(root_agent.tools)} tools loaded")

        session_service = InMemorySessionService()
        runner = Runner(
            agent=root_agent,
            app_name="test",
            session_service=session_service,
        )

        session = await session_service.create_session(
            app_name="test", user_id="tester"
        )

        message = types.Content(
            role="user",
            parts=[types.Part(text="What is the SPIN selling methodology?")],
        )

        print("\n📨 Sending test message: 'What is the SPIN selling methodology?'")
        print("   Waiting for response...\n")

        response_text = ""
        tool_calls = []

        async for event in runner.run_async(
            user_id="tester", session_id=session.id, new_message=message
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        response_text += part.text
                    if part.function_call:
                        tool_calls.append(part.function_call.name)

        if response_text:
            print(f"✅ Agent responded ({len(response_text)} chars)")
            print(f"   Tools called: {tool_calls or 'none'}")
            print(f"   Preview: {response_text[:200]}...")
        else:
            print("❌ Agent returned empty response")
            return False

        print("\n" + "=" * 50)
        print("ALL TESTS PASSED ✅")
        print("=" * 50)
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you've installed dependencies: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_agent())
    sys.exit(0 if success else 1)
