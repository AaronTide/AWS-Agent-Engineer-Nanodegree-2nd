# Demo: Strands SDK + AgentCore Runtime

## Topic
The simplest possible WanderBot — one Strands `Agent`, one built-in tool, wrapped in a `BedrockAgentCoreApp` and deployed to AgentCore Runtime.

## Why This Lesson
Every lesson that follows — tools, gateways, memory, browsers, RAG, observability — sits on top of this pattern. Get this right and the rest of the course is additive.

## The Four Pieces

```
BedrockAgentCoreApp      ← the runtime container
  └── @app.entrypoint    ← the function that handles every request
        └── Agent        ← Strands orchestration (LLM + tool loop)
              ├── BedrockModel   ← us.amazon.nova-2-lite-v1:0
              └── calculator     ← built-in Strands tool
```

## Deployment

```bash
pip install -r requirements.txt
agentcore configure
agentcore deploy
```

`agentcore configure` generates two artifacts for you:

- `.bedrock_agentcore.yaml` — the deployment config (entry file, container settings, IAM, ECR, auth)
- `Dockerfile` — the container image

`agentcore deploy` pushes your source to S3, kicks off a CodePipeline build, lands the image in ECR, and rolls the runtime.

## Run the Demo

```bash
agentcore invoke '{"message": "Hello! What can WanderBot help me with?"}'
agentcore invoke '{"message": "A flight costs $349. Hotel is $145/night for 4 nights. Transfers are $35 each way. What is my total?"}'
agentcore invoke '{"message": "My flight departs at 14:30 and arrives at 22:45. How many hours is that?"}'
```

The calculator tool fires automatically whenever the agent needs a number it can't trust itself to compute.

## Key Files
| File | Purpose |
|------|---------|
| `demo.py` | Full working WanderBot |
| `requirements.txt` | Runtime dependencies |
