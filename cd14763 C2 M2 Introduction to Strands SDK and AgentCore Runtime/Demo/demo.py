"""
================================================================================
WanderBot — DEMO: Strands SDK + AgentCore Runtime
================================================================================
"""

import logging

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent
from strands.models import BedrockModel
from strands_tools import calculator  # built-in Strands tool

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("WanderBot.AgentCoreRuntime")

# ---------------------------------------------------------------------------
# AgentCore app instance — the runtime container for our agent.
# ---------------------------------------------------------------------------
app = BedrockAgentCoreApp()

# ---------------------------------------------------------------------------
# Foundation model — Amazon Nova 2 Lite via a cross-region inference profile.
# Optional tuning: temperature=0.1, max_tokens=1024
# ---------------------------------------------------------------------------
MODEL_ID = "us.amazon.nova-2-lite-v1:0"

model = BedrockModel(model_id=MODEL_ID)

SYSTEM_PROMPT = """You are WanderBot, the AI travel assistant for Horizon Travel.

Horizon offers flights (Economy Lite, Economy Flex, Business), hotel bookings,
travel insurance, and the Horizon Rewards loyalty programme.

When asked to calculate anything — costs, tips, totals, durations, percentages —
use the calculator tool. Keep answers friendly, concise, and travel-focused."""


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
