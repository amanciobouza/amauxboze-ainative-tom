# Tasks

## 1. Review gate

- [x] 1.1 Confirm business intent and resolve open product decisions in design.md.
- [x] 1.2 Review proposal/design/spec scenarios against failure cases and dependencies; approve scope before application implementation.

## 2. Implementation (dependency order)

- [ ] 2.1 Define normalized run/stage/approval/event contracts and map all five workflow states and decisions.
- [ ] 2.2 Extend control-plane persistence plan with injectable durable engine checkpoints and atomic approval revisions.
- [ ] 2.3 Implement run queries, replayable event stream and revision-aware commands through WorkflowService.
- [ ] 2.4 Implement durable action identity/outcome and reconciliation behavior for uncertain results.
- [ ] 2.5 Build run list/detail, timeline, artifacts, approval and allowed recovery controls.
- [ ] 2.6 Test restart at every gate, stale/duplicate decisions, effect-before-checkpoint failure, retries, SSE gaps and redaction.

## 3. Verification

- [ ] 3.1 Validate OpenSpec structure and manually review requirement/scenario completeness.
- [ ] 3.2 Run relevant backend, contract and UI tests including specified failure paths.
- [ ] 3.3 Demonstrate feature with authoritative data and verify approvals/provider neutrality.
- [ ] 3.4 Record evaluation evidence, CI results and real task completion; archive only after acceptance.

## Consolidated delivery record

The authorized local-v1 implementation and verified completion checklist are in `implement-complete-local-app/tasks.md`; evidence and explicit integration limits are in `docs/ImplementationVerification.md`. Original broader acceptance items remain unchecked where they combine unverified failure cases, remote CI, or post-delivery acceptance. These changes are not archived.
