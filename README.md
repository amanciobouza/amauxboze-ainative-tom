# Amaux Bozé — AI Native Company

This repository contains the software, agent definitions, skills, workflows, schemas, tests, and technical architecture for operating Amaux Bozé as an AI-native micro watch brand.

## Run the local application

```powershell
.\run-local.ps1
```

Open the full Company OS at `http://127.0.0.1:3000`.
Use `-Production` to serve the built app on port 8000 instead.
See [Local application guide](docs/LocalApplication.md) for features, live models,
simulation, persistence, approval semantics and verification.

## Project constants

- **Obsidian Vault:** `C:\Users\amanc\OneDrive\ObsidianVaults\Amaux Bozé`
- **LM Studio Server:** `http://127.0.0.1:1234`
- **Repository:** `https://github.com/amanciobouza/amauxboze-ainative-tom`

## Operating principles

- Obsidian is the company knowledge base and organizational memory.
- LangGraph orchestrates multi-agent workflows and business processes.
- Skills define reusable capabilities.
- Tools define controlled access to external systems.
- LM Studio provides local LLMs; OpenAI and Anthropic may be used selectively.
- Software development is spec-driven using OpenSpec.
- Human approval gates protect consequential actions such as publishing, pricing, production, and outbound customer communication.

## Separation of concerns

- **Obsidian:** business knowledge, organization, decisions, learnings, policies, process descriptions.
- **GitHub:** code, OpenSpec, LangGraph graphs, agent definitions, skills, tools, schemas, tests, infrastructure.
