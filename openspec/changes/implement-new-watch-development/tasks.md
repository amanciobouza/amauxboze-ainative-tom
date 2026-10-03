# Tasks

## 1. Workflow State

- [ ] 1.1 Define NewWatchDevelopmentState
- [ ] 1.2 Define typed artifact model
- [ ] 1.3 Define workflow terminal and error states

## 2. Skills

- [ ] 2.1 Add define-product-brief skill for Elena
- [ ] 2.2 Add research-watch-opportunity skill for Nora
- [ ] 2.3 Add design-watch-concept skill for Lucien
- [ ] 2.4 Add review-brand-fit skill for Élodie
- [ ] 2.5 Add review-commercial-fit skill for Marc
- [ ] 2.6 Add review-customer-fit skill for Sophie
- [ ] 2.7 Add integrate-watch-recommendation skill for Elena
- [ ] 2.8 Add define-watch-spec skill for Lucien

## 3. Agent Permissions

- [ ] 3.1 Add new skills to agent manifests
- [ ] 3.2 Validate agent-to-skill authorization
- [ ] 3.3 Validate Obsidian read/write permissions

## 4. LangGraph Implementation

- [ ] 4.1 Implement intent definition node
- [ ] 4.2 Implement evidence gathering node
- [ ] 4.3 Implement product concept node
- [ ] 4.4 Implement brand review node
- [ ] 4.5 Implement commercial review node
- [ ] 4.6 Implement customer perspective node
- [ ] 4.7 Implement integrated recommendation node
- [ ] 4.8 Implement founder gate 1
- [ ] 4.9 Implement final specification node
- [ ] 4.10 Implement production approval gate
- [ ] 4.11 Implement reject/hold/revise routing
- [ ] 4.12 Implement error handling and retry metadata

## 5. Obsidian Persistence

- [ ] 5.1 Define workflow workspace paths
- [ ] 5.2 Persist stage artifacts
- [ ] 5.3 Persist founder decisions
- [ ] 5.4 Persist final product specification
- [ ] 5.5 Ensure writes contain trace metadata

## 6. Tests

- [ ] 6.1 Test happy path through both founder gates
- [ ] 6.2 Test revision path
- [ ] 6.3 Test rejection path
- [ ] 6.4 Test resume does not repeat completed stages
- [ ] 6.5 Test unauthorized agent/skill combinations
- [ ] 6.6 Test Obsidian persistence

## 7. Validation

- [ ] 7.1 Validate OpenSpec artifacts
- [ ] 7.2 Run full automated test suite
- [ ] 7.3 Demonstrate one end-to-end watch development run with mocked model execution
- [ ] 7.4 Review before connecting live LM Studio execution
