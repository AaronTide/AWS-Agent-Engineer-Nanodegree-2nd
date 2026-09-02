# Exercise: Strands SDK + AgentCore Runtime

## Overview
Build and deploy the first version of WanderBot. One Strands `Agent`, one built-in `calculator` tool, one `BedrockAgentCoreApp` — running on AgentCore Runtime.

**Estimated time:** 20 minutes

## Learning Objectives
1. Scaffold a `BedrockAgentCoreApp` with a single `@app.entrypoint` function
2. Configure a Strands `Agent` with a `BedrockModel` and a built-in tool
3. Use the `agentcore` CLI — `configure`, `dev`, `invoke`, `deploy` — to test and ship
4. Understand the deployment pipeline: source → S3 → CodePipeline → ECR → Runtime

## Prerequisites
- AWS account with Bedrock model access for Amazon Nova 2 Lite
- `agentcore` CLI installed (`pip install bedrock-agentcore-starter-toolkit`)

## Exercise Steps

### Step 1 — Imports
Import `BedrockAgentCoreApp`, `Agent`, `BedrockModel`, and `calculator`.

### Step 2 — App instance
`app = BedrockAgentCoreApp()`

### Step 3 — Model
`model = BedrockModel(model_id=MODEL_ID)`

### Step 4 — System prompt
Describe WanderBot's role, Horizon's services, when to use the calculator, and the tone.

### Step 5 — Wire the agent inside `invoke()`
```python
agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[calculator],
)
response = agent(user_message)
return response
```

## Test Locally First

```bash
pip install -r requirements.txt
agentcore configure
agentcore dev
```

In a second terminal:

```bash
agentcore invoke --dev '{"message": "A flight costs $349. Hotel is $175/night for 4 nights. Total?"}'
```

`agentcore dev` runs the container locally against your AWS credentials — same code path as production, no deploy needed.

## Deploy

```bash
agentcore deploy --auto-update-on-conflict
```

The `--auto-update-on-conflict` flag is useful when you reconfigure with a new entry file (e.g. from `demo.py` to `starter.py`) — it updates the existing runtime in place instead of erroring.

### What `deploy` actually does
1. Zips your source and uploads to S3
2. Triggers a CodePipeline build that produces a Docker image
3. Pushes the image to ECR
4. Rolls the AgentCore Runtime to the new image

You can watch each stage in the AWS Console — S3 → CodePipeline → ECR → Bedrock AgentCore.

## Invoke

```bash
agentcore invoke '{"message": "How do I contact Horizon Travel customer support?"}'
agentcore invoke '{"message": "My trip is $349 flight + $175/night × 4 nights + $59 insurance. What is my total?"}'
```

## A Note on the Dockerfile

`agentcore configure` generates a `Dockerfile` from your entry file. If you reconfigure with a different entry file, the YAML updates but the Dockerfile doesn't regenerate automatically — edit it manually before the next deploy.

## Files
| File | Purpose |
|------|---------|
| `starter.py` | Starter — 5 TODOs |
| `solution.py` | Reference solution |
| `requirements.txt` | Runtime dependencies |

## Hints

| Issue | Hint |
|-------|------|
| `agentcore dev` fails to start | Check if you have installed the required modules locally |
| Deploy errors with a conflict | Re-run with `--auto-update-on-conflict` |
| Agent ignores the calculator | Make the system prompt explicit: "always use the calculator tool" |
