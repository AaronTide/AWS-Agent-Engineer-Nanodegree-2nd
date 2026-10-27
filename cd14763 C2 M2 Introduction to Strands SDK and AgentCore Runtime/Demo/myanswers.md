# Demo: Strands SDK + AgentCore Runtime

```
Note: I'm using Powershell on Windows so the commands differ a bit from the Linux Commands given in the readme.
I've included all my relevant commands here.
```

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

1) Installing and configuring AWS CLI on local machine:

```
   irm https://awscli.amazonaws.com/v2/install.ps1 | iex
   aws --version
   aws configure
```
Put in your aws credentials: 

```
  AWS Access Key ID:
  AWS Secret Access Key:
  AWS Session Token:
  Default region name: us-east-1
  Default output format: json 
```

2) Navigate to the correct directory, create a venv with Python 3.10
```
cd 'Exercises\cd14763 C2 M2 Introduction to Strands SDK and AgentCore Runtime\Demo'
py -3.10 -m venv --without-pip .venv
``` 
   
 3) Install pip, uv 

```
 Invoke-WebRequest https://bootstrap.pypa.io/get-pip.py -OutFile get-pip.py
 .\.venv\Scripts\python.exe get-pip.py
 powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Restart your editor to make sure uv and pip is installed properly


4) Using the previous version of the Agentcore CLI to follow the course:
```
uv pip install bedrock-agentcore-starter-toolkit
uv pip install -r requirements.txt
```

5) Configuring and deploying Wanderbot using Agentcore CLI 


```
agentcore configure
```

**Refer to these settings for your Agent's configuration:**

**Agent Details** 

│ Agent Name: WanderBot  

│ Deployment: container   

│ Region: us-east-1                                                                                                                                                          │                                                                                                                                                    │
     

**Configuration**  

│ Execution Role: Auto-create      

│ Network Mode: Public       

│ ECR Repository: Auto-create     

│ Authorization: IAM (default) 
│

```
agentcore deploy
```


`agentcore configure` generates two artifacts for you:

- `.bedrock_agentcore.yaml` — the deployment config (entry file, container settings, IAM, ECR, auth)
- `Dockerfile` — the container image

`agentcore deploy` pushes your source to S3, kicks off a CodePipeline build, lands the image in ECR, and rolls the runtime.



**If you see: X Codebuild failed with status: STOPPED:**

Try this:


1. Find the codebuild.py file
   
Run this command in PowerShell:

```
python -c "import importlib.util; s=importlib.util.find_spec('bedrock_agentcore_starter_toolkit.services.codebuild'); print(s.origin if s else 'Module not found')"
```

If the module is installed in this environment, you'll get a path resembling:

D:\...\ .venv\Lib\site-packages\bedrock_agentcore_starter_toolkit\services\codebuild.py



2. Check whether the problematic setting exists
   
Copy the path returned by the previous command into $file below:

```
$file = "PASTE_THE_ACTUAL_PATH_HERE"
Select-String -Path $file -Pattern "BUILD_GENERAL1_MEDIUM|computeType"
```

If you see a line resembling:
"computeType": "BUILD_GENERAL1_MEDIUM"
then the workaround may apply to your installed toolkit.

3. If the exact setting exists, apply the workaround safely
   
Before changing the toolkit, create a backup. 

Run:

```
Copy-Item $file "$file.bak"
```



Then use this PowerShell command to replace the exact setting, but only if it occurs once:

```
$content = Get-Content $file -Raw
$old = '"computeType": "BUILD_GENERAL1_MEDIUM"'
$new = '"computeType": "BUILD_GENERAL1_SMALL"'

$count = ([regex]::Matches($content, [regex]::Escape($old))).Count

if ($count -eq 1) {
    $content = $content.Replace($old, $new)
    Set-Content -Path $file -Value $content -NoNewline
    Write-Host "Updated compute type to BUILD_GENERAL1_SMALL"
} else {
    Write-Host "Expected exactly one match; found $count. No changes made."
}
```

Why the caution? 

The workaround was reported to solve a specific lab-account restriction. It isn't a universal fix for every STOPPED CodeBuild deployment.


## Answers From WanderBot

**First Question:**

```
agentcore invoke '{\"message\": \"How do I contact Horizon Travel customer support?\"}'
```

Response:

```
## Horizon Travel Customer Support Contact Information

**Phone Support:**
- **North America:** 1-800-HORIZON (1-800-467-4466)
- **International:** +1-416-555-0199

**Email Support:**
- **General inquiries:** support@horizontravel.com
- **Booking questions:** bookings@horizontravel.com
- **Rewards program:** rewards@horizontravel.com

**Live Chat:**
Available 24/7 on our website at (https://www.horizontravel.com) - look for the chat icon in the bottom right corner.

**Office Locations:**
- **Headquarters:** 100 Travel Way, Toronto, ON M5V 3L4, Canada
- **New York Office:** 500 Fifth Avenue, New York, NY 10110, USA

**Hours of Operation:**
- **Phone & Live Chat:** 24 hours a day, 7 days a week
- **Office Hours:** Monday-Friday 9:00 AM - 6:00 PM local time

For fastest service, please have your booking reference number ready when contacting support.
```

**Second Question**

```
agentcore invoke '{\"message\": \"A flight costs $349. Hotel is $145/night for 4 nights. Transfers are $35 each way. What is my total?\"}'
```

Response:

```
Your total cost will be **$999** — this includes:

- Flight: $349
- Hotel (4 nights): $580
- Transfers (there and back): $70

Safe travels with Horizon Travel! ✈️🏨
```




The calculator tool fires automatically whenever the agent needs a number it can't trust itself to compute.

## Key Files
| File | Purpose |
|------|---------|
| `demo.py` | Full working WanderBot |
| `requirements.txt` | Runtime dependencies |

