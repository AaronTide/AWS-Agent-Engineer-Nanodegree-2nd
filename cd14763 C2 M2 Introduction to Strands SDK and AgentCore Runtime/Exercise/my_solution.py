"""
================================================================================
WanderBot — EXERCISE SOLUTION: Strands SDK + AgentCore Runtime
================================================================================
Reference solution for the exercise. A Strands Agent with the built-in
calculator tool, wrapped in a BedrockAgentCoreApp, ready for AgentCore Runtime.

HOW TO RUN
----------
  agentcore configure
  agentcore dev
  agentcore invoke --dev '{"message": "A round-trip flight costs $349. Hotel is $175/night for 4 nights. Total?"}'

  agentcore deploy --auto-update-on-conflict
  agentcore invoke '{"message": "How do I contact Horizon Travel customer support?"}'
================================================================================
"""

import logging

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent
from strands.models import BedrockModel
from strands_tools import calculator

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("WanderBot.AgentCoreRuntime")

# ---------------------------------------------------------------------------
# AgentCore app instance
# ---------------------------------------------------------------------------
app = BedrockAgentCoreApp()

# ---------------------------------------------------------------------------
# Foundation model — Amazon Nova 2 Lite via a cross-region inference profile.
# Optional tuning: temperature=0.1, max_tokens=1024
# ---------------------------------------------------------------------------
MODEL_ID = "us.amazon.nova-2-lite-v1:0"

model = BedrockModel(model_id=MODEL_ID)

SYSTEM_PROMPT = """You are WanderBot, the official AI travel assistant for Horizon Travel.

ABOUT HORIZON TRAVEL
Horizon Travel offers flights, hotel bookings, travel insurance, and the
Horizon Rewards loyalty programme (Silver, Gold, Platinum tiers).

FARE CLASSES
- Economy Lite : no changes, no refunds, 1 cabin bag
- Economy Flex : 1 free change, 85% refund (7+ days), 1 checked bag (23 kg)
- Business     : unlimited changes, full refund, 2 checked bags (32 kg), lounge access

TOOL USE
When asked to calculate costs, points, durations, or any numeric value,
always use the calculator tool for accuracy.

STYLE
Friendly, concise, travel-focused. Use bullet points for lists of options.
Sign off farewells with "Happy travels! ✈️".

Do not invent specific flight schedules or prices — direct customers to
horizontravel.com for live pricing and availability."""


@app.entrypoint
async def invoke(payload: dict, context=None):
    """WanderBot — Agent entry point."""
    user_message = payload.get("message", "Hello!")
    logger.info("User: %s", user_message[:80])

    agent = Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[calculator],
    )
    response = agent(user_message)
    return response


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run()
