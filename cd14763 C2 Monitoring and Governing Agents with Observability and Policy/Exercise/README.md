# Exercise: AgentCore Native Observability

## Overview
Wire up WanderBot with two tools, deploy it, and navigate the CloudWatch GenAI Observability Dashboard to read the traces your agent produces.

**Estimated time:** 15 minutes

## Learning Objectives
1. Enable AgentCore observability with a single dependency (`aws-opentelemetry-distro`)
2. Understand how AgentCore groups invocations by session in CloudWatch
3. Read agent invocation traces — model, token counts, latency, error traces
4. Read tool call spans — inputs, outputs, duration
5. Know where to go further with per-service log delivery (Gateway, Memory, built-in tools)

## Prerequisites
- AgentCore Runtime deployed to your AWS account
- CloudWatch access in the same region

## How Observability Works

```
              agentcore deploy
                     │
             Agent invocation span
                     │
         ┌───────────┴───────────┐
         │                       │
  search_flights span     search_hotels span
  (inputs + output)      (inputs + output)
```

Because this agent runs inside **AgentCore Runtime**, observability is built in. AgentCore uses OpenTelemetry (ADOT) to instrument every invocation automatically. Traces go to X-Ray and surface in the CloudWatch GenAI Observability Dashboard.

## Exercise Steps

### Step 1 — Uncomment `search_flights`
Reads `datasets/flights.json`; filters by origin, destination, and status.

### Step 2 — Uncomment `search_hotels`
Reads `datasets/hotels.json`; filters by city, availability, and `price_per_night_usd`.

### Step 3 — Wire the agent
```python
agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[search_flights, search_hotels],
)
response = agent(user_message)
return response
```

## Deploy and Test

```bash
pip install -r requirements.txt
agentcore configure -e starter.py -n WanderBot -dt container -rf requirements.txt --disable-memory -er $ER -ecr $ECR_URI --non-interactive
agentcore deploy
```

Because the agent is deployed as a container, consecutive `agentcore invoke` calls share the same live runtime session — CloudWatch groups them automatically. To start a fresh session, call `agentcore stop-session` between invokes.

```bash
# Session 1 — two turns grouped automatically
agentcore invoke '{"message": "Find flights from London to Tokyo"}'
agentcore invoke '{"message": "Hotels in Tokyo under $200/night"}'

# Break the session, start a fresh one
agentcore stop-session

# Session 2
agentcore invoke '{"message": "Flights from New York to Rome"}'
agentcore invoke '{"message": "Hotels in Rome"}'
```

## Observing in CloudWatch

Navigate to: **CloudWatch → GenAI Observability → Bedrock AgentCore**

| View | What to look for |
|------|-----------------|
| **Sessions** | Your session IDs, with all turns grouped together |
| **Traces** | Click a trace to expand the span tree |
| **Tool spans** | Each tool call is a child span with its inputs and output |
| **Model & tokens** | Model name and input/output token counts on the invocation span |
| **Errors** | Red error markers bubble up to the top of the trace |

### What a trace looks like

```
AgentInvocation   total ~3.2s | model: nova-2-lite | tokens 512 in / 128 out
  ├── search_flights   origin=LHR, destination=HND → 3 results, 120ms
  └── search_hotels    city=Tokyo, max_price=200 → 2 results, 95ms
```

## Bonus — Other Tabs in the Dashboard

The GenAI Observability Dashboard has a tab per AgentCore service, not just the agent runtime:

- **Built-in Tools** — Browser and Code Interpreter
- **Gateway** 
- **Identity** 
- **Memory** 

Each tab shows basic utilisation metrics out of the box (sessions started, invocations, compute, memory). **Traces are opt-in per resource** — enable tracing on the resource and the trace view fills up. Leave it off and you only get the headline metrics.

In this course we've enabled tracing on the Memory resource — try clicking the Memory tab and you'll see traces for `create_event` calls and memory retrievals. The other tabs will show metrics but empty trace views.

## A Note on `aws-opentelemetry-distro`

The documented way to enable observability is to add `aws-opentelemetry-distro` to `requirements.txt`. But when you deploy via `agentcore configure && agentcore deploy`, the starter toolkit adds it into the generated Dockerfile for you — so it is already in your container image whether or not you listed it in `requirements.txt`. If you build your own image from scratch, make sure to include the distro yourself.

## Hints

| Issue | Hint |
|-------|------|
| Traces not appearing | Confirm `aws-opentelemetry-distro` is in `requirements.txt` |
| Sessions view empty | Make sure you invoked via AgentCore (not local `app.run()`) |
| Sessions don't group | Consecutive invokes share the runtime session automatically; run `agentcore stop-session` to break it |
| Tool spans missing | Confirm the agent actually called the tool — check the response for tool use |

## Files
| File | Purpose |
|------|---------|
| `starter.py` | Starter — 3 TODOs |
| `solution.py` | Reference solution |
| `datasets/flights.json`, `datasets/hotels.json` | Mock travel data |
| `requirements.txt` | Runtime dependencies (includes `aws-opentelemetry-distro`) |
