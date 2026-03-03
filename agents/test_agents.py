#!/usr/bin/env python3
"""
Quick smoke test for BorrowHood Gemini agents.

Usage:
    cd BorrowHood
    source agents/.venv/bin/activate
    python -m agents.test_agents
"""

import asyncio
import os
import warnings

# Suppress SSL warnings for self-signed cert on Hetzner
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

# Load env
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from google.adk.runners import InMemoryRunner
from google.genai import types

from .agent import root_agent


async def test_agent(query: str, label: str):
    """Send a single query to the root agent and print the response."""
    print(f"\n{'='*60}")
    print(f"TEST: {label}")
    print(f"QUERY: {query}")
    print(f"{'='*60}")

    runner = InMemoryRunner(agent=root_agent, app_name="borrowhood_test")
    session = await runner.session_service.create_session(
        app_name="borrowhood_test", user_id="test_user"
    )

    user_msg = types.Content(
        role="user",
        parts=[types.Part(text=query)],
    )

    response_text = ""
    async for event in runner.run_async(
        user_id="test_user",
        session_id=session.id,
        new_message=user_msg,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    response_text += part.text

    if response_text:
        # Truncate long responses for readability
        display = response_text[:1000]
        if len(response_text) > 1000:
            display += f"\n... ({len(response_text)} chars total)"
        print(f"\nRESPONSE:\n{display}")
        print(f"\nPASS")
    else:
        print(f"\nNO RESPONSE")
        print(f"\nFAIL")

    return response_text


async def main():
    print("BorrowHood Gemini Agents -- Smoke Test")
    print(f"API Key: ...{os.environ.get('GOOGLE_API_KEY', 'NOT SET')[-8:]}")
    print(f"BH URL: {os.environ.get('BH_BASE_URL', 'NOT SET')}")

    # Test 1: Listing Assistant
    await test_agent(
        "I want to list a Bosch power drill, model GSB 18V. It's in good condition, "
        "I've had it for 2 years. Help me create a listing.",
        "Smart Listing Assistant"
    )

    # Test 2: Review Analyzer
    await test_agent(
        "Analyze the reviews for Sally. What's her reputation like?",
        "Review Sentiment Analyzer"
    )

    # Test 3: Concierge - item search
    await test_agent(
        "I need something to cut tree branches. What's available?",
        "AI Concierge - Item Search"
    )

    # Test 4: Concierge - language search
    await test_agent(
        "Who speaks Italian in the neighborhood?",
        "AI Concierge - Language Search"
    )

    # Test 5: General BorrowHood question
    await test_agent(
        "What is BorrowHood?",
        "General Knowledge"
    )

    print(f"\n{'='*60}")
    print("ALL TESTS COMPLETE")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
