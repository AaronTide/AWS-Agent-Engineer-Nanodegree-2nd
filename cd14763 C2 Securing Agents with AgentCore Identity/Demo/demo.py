"""
================================================================================
WanderBot — EXERCISE: AgentCore Identity
================================================================================
"""

import logging

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from mcp.client.streamable_http import streamable_http_client
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp.mcp_client import MCPClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("WanderBot.AgentCoreIdentity")

app = BedrockAgentCoreApp()
model = BedrockModel(model_id="us.amazon.nova-2-lite-v1:0")

# TODO: Set this to your Gateway endpoint here
GATEWAY_ENDPOINT = "Gateway URL goes here"

SYSTEM_PROMPT = """You are WanderBot, the AI travel assistant for Horizon Travel.

All of your tools are provided dynamically through the AgentCore Gateway. Discover the available tools at runtime and use them to answer customer questions about bookings, travel plans, and account details.

Guidelines:
- Rely on the tools available to you through the Gateway — do not assume capabilities that aren't exposed as tools.
- Choose the most relevant tool for each request and call it with the required parameters.
- If a request needs information across multiple tools, call them in sequence and combine the results.
- If no available tool can fulfil a request, say so clearly instead of guessing.
- Ask clarifying questions when the user's request is ambiguous or missing required details.
- Present results in a clear, concise, customer-friendly format."""


@app.entrypoint
async def invoke(payload: dict, context=None) -> dict:
    """WanderBot — AgentCore Identity"""
    user_message = payload.get("message", "Hello!")

    logger.info("User: %s", user_message[:80])

    client = MCPClient(lambda: streamable_http_client(url=GATEWAY_ENDPOINT))
    with client:
        tools = client.list_tools_sync()
        logger.info("Discovered %d tools from Gateway", len(tools))

        agent = Agent(
            model=model,
            system_prompt=SYSTEM_PROMPT,
            tools=tools,
        )
        response = agent(user_message)

    return response


if __name__ == "__main__":
    app.run()
