# Exercise: AgentCore Identity

## Overview
In this exercise, you will secure a new API target on the Gateway. Unlike previous lesson, **no code changes are required** — the agent already works for any tool exposed by the Gateway. The exercise is entirely infrastructure: deploy a REST API that requires an API key, store that key in AgentCore Identity, and add the API as a target in the existing Gateway.

This is the core message of the lesson: credential management lives in the infra layer, not in the agent code.

**Estimated time:** 25 minutes (AWS console)

## Learning Objectives
1. Deploy a REST API in API Gateway with Lambda proxy integration
2. Create and associate an API key and a usage plan
3. Store an API key as a credential in AgentCore Identity
4. Add an API Gateway target to the existing AgentCore Gateway with Identity-backed auth
5. Verify that the existing agent code works against the new secured target without modification

## Architecture
```
WanderBot (Strands Agent)
    ↓  tool call (MCP protocol)
AgentCore Gateway  (No Authentication)
    ├── Lambda target       → wanderbot-booking-tools
    └── API Gateway target  → /loyalty/{member_id}
            ↓  x-api-key (injected from AgentCore Identity)
        API Gateway  (API key required)
            ↓  Lambda proxy
        wanderbot-loyalty-points Lambda
```

## Prerequisites
- Completed AgentCore Gateway with Lambda target
- Existing `wanderbot-gateway`
- AWS credentials configured

---

## Exercise Steps

### Step 1: Deploy the Loyalty Lambda
Deploy `lambda/loyalty_points_api.py` as a Lambda function:
- **Function name:** `wanderbot-loyalty-points`
- **Runtime:** Python 3.14
- **Handler:** `loyalty_points_api.lambda_handler`

### Step 2: Create the REST API
In API Gateway console:
1. Create **REST API** named `wanderbot-loyalty-api`
2. Create resource `/loyalty` → child `{member_id}` → method **GET**
3. Integration: **Lambda proxy** → `wanderbot-loyalty-points`
4. On the GET method → **Method Request**:
   - Enable **API key required: true**
   - Operation name: `get_loyalty_account`
5. **Deploy API** to a stage (e.g. `prod`)

### Step 3: Create API Key and Usage Plan
1. API Gateway → **API Keys** → Create API key → name: `wanderbot-loyalty-key` → note the value
2. API Gateway → **Usage Plans** → Create: name `wanderbot-loyalty-plan`
3. Associate the usage plan with your API's `prod` stage
4. Add the API key to the usage plan

### Step 4: Store the API Key in AgentCore Identity
In the AWS Console → Bedrock AgentCore → **Identity**:
1. **Create credential** → type: **API Key**
2. Name: `wanderbot-loyalty-api-key`
3. Paste the API key value from Step 3

### Step 5: Add the API Gateway Target to the Gateway
In the existing `wanderbot-gateway` → **Targets** → Add target:
- Type: **API Gateway**
- Select the API, Stage and Operation from Step 2
- Authorization: **API Key** → select the Identity from Step 4
- Header parameter name: `x-api-key`

---

## Run the Agent

The agent code does not need any changes. Set `GATEWAY_ENDPOINT` in `starter.py` to your existing Gateway URL and deploy.

```bash
pip install -r requirements.txt
```

```bash
ER=$(python -c 'import yaml,sys; print(yaml.safe_load(open(".bedrock_agentcore.yaml"))["agents"]["WanderBot"]["aws"]["execution_role"])')
ECR_URI=$(python -c 'import yaml,sys; print(yaml.safe_load(open(".bedrock_agentcore.yaml"))["agents"]["WanderBot"]["aws"]["ecr_repository"])')
agentcore configure -e starter.py -n WanderBot -dt container -rf requirements.txt --disable-memory -er $ER -ecr $ECR_URI --non-interactive
agentcore deploy
```

```bash
agentcore invoke '{"message": "What are the loyalty points for member hz-001?"}'
```

```bash
agentcore invoke '{"message": "Look up Horizon Rewards account hz-002"}'
```

## Key Insight
Nothing in the agent code changed. The whole security story — API key storage, rotation, per-request injection — is handled by the Gateway plus AgentCore Identity. The agent stays focused on the conversation.

## Common Errors
| Error | Fix |
|-------|-----|
| `403 Forbidden` on loyalty tool | API key not associated with the Usage Plan, or usage plan not bound to the stage |
| Tool not discovered | Check the API Gateway target is **Active** in the Gateway console |
| `Unauthorized` from the target | Identity not wired to the target, or header parameter name not `x-api-key` |

## Files
| File | Purpose |
|------|---------|
| `lambda/loyalty_points_api.py` | Lambda behind the loyalty REST API |
| `starter.py` | Agent code (no changes needed) |
| `solution.py` | Same as starter |
