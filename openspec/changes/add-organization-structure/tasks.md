# Tasks

## 1. Review gate

- [x] 1.1 Confirm business intent and resolve open product decisions in design.md.
- [x] 1.2 Review proposal/design/spec scenarios against failure cases and dependencies; approve scope before application implementation.

## 2. Implementation (dependency order)

- [ ] 2.1 Define and validate organization/relationship contracts and canonical configuration ownership.
- [ ] 2.2 Seed proposed human/agent/department mapping after product review; reconcile docs/OrganizationMap.md.
- [ ] 2.3 Expose read-only organization service/API with structured validation errors.
- [ ] 2.4 Build hierarchy and accessible list with department filters and agent navigation.
- [ ] 2.5 Test duplicate IDs, cycles, missing references, correct identities and unchanged authorization.

## 3. Verification

- [ ] 3.1 Validate OpenSpec structure and manually review requirement/scenario completeness.
- [ ] 3.2 Run relevant backend, contract and UI tests including specified failure paths.
- [ ] 3.3 Demonstrate feature with authoritative data and verify approvals/provider neutrality.
- [ ] 3.4 Record evaluation evidence, CI results and real task completion; archive only after acceptance.

## Consolidated delivery record

The authorized local-v1 implementation and verified completion checklist are in `implement-complete-local-app/tasks.md`; evidence and explicit integration limits are in `docs/ImplementationVerification.md`. Original broader acceptance items remain unchecked where they combine unverified failure cases, remote CI, or post-delivery acceptance. These changes are not archived.
