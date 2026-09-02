"""
================================================================================
WanderBot — DEMO: No Validation
================================================================================
"""

import json
import logging
from pathlib import Path

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, tool
from strands.models import BedrockModel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("WanderBot.StructuredOutputs")

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "datasets"
FLIGHTS_FILE = DATA_DIR / "flights_broken.json"

app = BedrockAgentCoreApp()

MODEL_ID = "us.amazon.nova-2-lite-v1:0"
model = BedrockModel(model_id=MODEL_ID)

SYSTEM_PROMPT = """You are WanderBot, the AI travel assistant for Horizon Travel.

AVAILABLE TOOLS
1. search_flights — Search Horizon Travel flights by route and date

GUIDELINES
- Always use tools to fetch real data instead of guessing
- When a customer asks about flights, use search_flights with the correct IATA codes
- Be concise, structured, and helpful

IATA CODE QUICK REFERENCE
LHR = London Heathrow | CDG = Paris Charles de Gaulle | JFK = New York JFK
MIA = Miami | LAX = Los Angeles | BCN = Barcelona | FCO = Rome Fiumicino"""


@tool
def search_flights(origin: str, destination: str, date: str) -> str:
    """
    Search for available Horizon Travel flights between two airports on a specific date.

    Use this tool when a customer asks about flight availability, times, or prices.

    Args:
        origin      : IATA departure airport code (e.g. 'LHR', 'JFK')
        destination : IATA arrival airport code (e.g. 'CDG', 'MIA')
        date        : Travel date in YYYY-MM-DD format (e.g. '2026-03-15')

    Returns:
        JSON string with flight results.
    """
    logger.info("search_flights called: %s → %s on %s", origin, destination, date)

    try:
        with open(FLIGHTS_FILE, encoding="utf-8") as f:
            flights = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error("Failed to load flights data: %s", e)
        return json.dumps({"error": "Flight database unavailable"})

    matches = [
        fl for fl in flights
        if fl.get("origin", "").upper() == origin.strip().upper()
        and fl.get("destination", "").upper() == destination.strip().upper()
        and fl.get("date", "") == date.strip()
    ]

    # No validation — whatever is in the JSON goes straight to the agent
    return json.dumps(matches, indent=2)


@app.entrypoint
async def invoke(payload, context=None):
    """WanderBot — no validation entry point."""

    user_message = payload.get("message", "Hello!")
    logger.info("User: %s", user_message[:100])

    agent = Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[search_flights],
    )

    response = agent(user_message)
    return response


if __name__ == "__main__":
    app.run()