# Tasks

## 1. Workflow State

- [x] 1.1 Define NewWatchDevelopmentState
- [x] 1.2 Define typed artifact model
- [x] 1.3 Define workflow terminal and error states

## 2. Skills

- [x] 2.1 Add define-product-brief skill for Elena
- [x] 2.2 Add research-watch-opportunity skill for Nora
- [x] 2.3 Add design-watch-concept skill for Lucien
- [x] 2.4 Add review-brand-fit skill for Élodie
- [x] 2.5 Add review-commercial-fit skill for Marc
- [x] 2.6 Add review-customer-fit skill for Sophie
- [x] 2.7 Add integrate-watch-recommendation skill for Elena
- [x] 2.8 Add define-watch-spec skill for Lucien

## 3. Agent Permissions

- [x] 3.1 Add new skills to agent manifests
- [x] 3.2 Validate agent-to-skill authorization
- [x] 3.3 Validate Obsidian read/write permissions

## 4. LangGraph Implementation

- [x] 4.1 Implement intent definition node
- [x] 4.2 Implement evidence gathering node
- [x] 4.3 Implement product concept node
- [x] 4.4 Implement brand review node
- [x] 4.5 Implement commercial review node
- [x] 4.6 Implement customer perspective node
- [x] 4.7 Implement integrated recommendation node
- [x] 4.8 Implement founder gate 1
- [x] 4.9 Implement final specification node
- [x] 4.10 Implement production approval gate
- [x] 4.11 Implement reject/hold/revise routing
- [ ] 4.12 Implement error handling and retry metadata

## 5. Obsidian Persistence

- [x] 5.1 Define workflow workspace paths
- [x] 5.2 Persist stage artifacts
- [x] 5.3 Persist founder decisions
- [x] 5.4 Persist final product specification
- [x] 5.5 Ensure writes contain trace metadata

## 6. Tests

- [x] 6.1 Test happy path through both founder gates
- [ ] 6.2 Test revision path
- [x] 6.3 Test rejection path
- [ ] 6.4 Test resume does not repeat completed stages
- [ ] 6.5 Test unauthorized agent/skill combinations
- [x] 6.6 Test Obsidian persistence

## 7. Validation

- [ ] 7.1 Validate OpenSpec artifacts
- [ ] 7.2 Run full automated test suite
- [ ] 7.3 Demonstrate one end-to-end watch development run with mocked model execution
- [ ] 7.4 Review before connecting live LM Studio execution
