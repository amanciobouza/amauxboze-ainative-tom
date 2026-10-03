# Obsidian Vault Structure

Target vault:

`C:\Users\amanc\OneDrive\ObsidianVaults\Amaux Bozé`

Recommended structure:

```text
Organization/
├── 00_Operating-Model.md
├── 01_Org-Chart.md
├── Agents/
├── Roles/
├── Decision-Rights/
└── Governance/

Processes/
├── Product-Development/
├── Product-Launch/
├── Content-Campaign/
├── Customer-Feedback/
└── Market-Intelligence/

Brand/
Products/
Customers/
Commerce/
Research/
Roblox/
Decisions/
Learnings/
Inbox/
```

## Source-of-truth rule

Obsidian owns business knowledge and operating documentation.

GitHub owns software implementation, agent runtime definitions, skills, schemas, tests, integrations, and OpenSpec artifacts.

When a software change is needed, first update or confirm the business intent in Obsidian, then create an OpenSpec change in GitHub before implementation.
