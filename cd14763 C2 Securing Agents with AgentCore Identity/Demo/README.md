# Demo: AgentCore Identity

## Topic
Secure an API Gateway target using an API key stored in AgentCore Identity

## Duration
~6 minutes

## What the Demo Shows
- A loyalty REST API (already deployed, API key required) added as an AgentCore Gateway target
- The target fails to return data when no Identity is configured
- Creating an API Key credential in AgentCore Identity
- Configuring the gateway target with that Identity and the `x-api-key` header
- The agent now calls the secured API transparently — code is unchanged

## Architecture

```
WanderBot (Strands Agent)
    ↓  MCPClient — same Gateway endpoint
AgentCore Gateway
    ├── Lambda target (direct)  → wanderbot-booking-tools
    └── API Gateway target      → /loyalty/{member_id}
            ↓  x-api-key header (injected from AgentCore Identity)
        API Gateway  (API key required)
            ↓  Lambda proxy
        wanderbot-loyalty-points Lambda
```

## Key Concepts

| Concept | Description |
|---------|-------------|
| **AgentCore Identity** | Secure credential store — API keys, OAuth tokens |
| **API Gateway target** | Gateway calls a REST API endpoint instead of a Lambda directly |
| **Transparent auth** | Gateway retrieves the key from Identity and injects the header per-request — the agent never sees it |
| **No code change** | Agent code is byte-for-byte the same |

## Pre-Bake (run before recording)
See `../PREBAKE.md`. It deploys:
- `wanderbot-loyalty-points` Lambda
- `wanderbot-loyalty-api` REST API with `GET /loyalty/{member_id}`, API key required, usage plan + key attached

## Demo Flow (recording)
1. Show the secured API with curl — 403 without key, 200 with key
2. Add the API Gateway as a target in the existing `wanderbot-gateway` **without** configuring auth
3. Invoke the agent — the loyalty tool call fails (gateway cannot reach the API)
4. AgentCore Identity → create credential type **API Key** → paste the key value
5. Gateway → loyalty target → edit auth configuration → select API Key → choose the Identity → header name `x-api-key`
6. Invoke the agent again — loyalty data comes back
7. Walk through `demo.py` — identical to previous lesson, only one extra tool in the system prompt

## Talking Points

> "The agent code didn't change. We added a secure API as a target and pointed it at a credential in Identity. The Gateway injects the header on every request."

> "Rotate the key in Identity — the Gateway picks it up on the next call. No redeployment."

## Files
| File | Purpose |
|------|---------|
| `demo.py` | Agent code |
| `lambda/loyalty_points_api.py` | Lambda behind the loyalty REST API |
