# Tasks

## 1. Review gate

- [ ] 1.1 Confirm business intent and resolve open product decisions in design.md.
- [ ] 1.2 Review proposal/design/spec scenarios against failure cases and dependencies; approve scope before application implementation.

## 2. Implementation (dependency order)

- [ ] 2.1 Define agent profile/activity/attempt projection contracts and freshness rules.
- [ ] 2.2 Connect approved biography sources through KnowledgeProvider and registry skill metadata.
- [ ] 2.3 Implement persistent per-agent activity/history query service and pagination.
- [ ] 2.4 Build profile, active assignments and history UI with links to runs/artifacts.
- [ ] 2.5 Test concurrent work, waiting/blocked states, missing profile data, stale stream, restart and redaction.

## 3. Verification

- [ ] 3.1 Validate OpenSpec structure and manually review requirement/scenario completeness.
- [ ] 3.2 Run relevant backend, contract and UI tests including specified failure paths.
- [ ] 3.3 Demonstrate feature with authoritative data and verify approvals/provider neutrality.
- [ ] 3.4 Record evaluation evidence, CI results and real task completion; archive only after acceptance.
