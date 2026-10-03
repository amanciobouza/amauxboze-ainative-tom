# Tasks

## 1. Backend Foundation

- [ ] 1.1 Add FastAPI application
- [ ] 1.2 Add API configuration and startup health checks
- [ ] 1.3 Add CORS/local frontend configuration
- [ ] 1.4 Add structured API error handling

## 2. Runtime Persistence

- [ ] 2.1 Define runtime repository interfaces
- [ ] 2.2 Add SQLite local database
- [ ] 2.3 Persist workflow run metadata
- [ ] 2.4 Persist approval requests
- [ ] 2.5 Persist runtime events
- [ ] 2.6 Persist idempotency records
- [ ] 2.7 Keep PostgreSQL migration boundary explicit

## 3. Workflow API

- [ ] 3.1 List available workflows
- [ ] 3.2 Start workflow
- [ ] 3.3 Get workflow run
- [ ] 3.4 List workflow runs
- [ ] 3.5 Resume approval interrupt
- [ ] 3.6 Resume error recovery
- [ ] 3.7 Stream workflow state/events

## 4. Organization API

- [ ] 4.1 List agents
- [ ] 4.2 Get agent details
- [ ] 4.3 Expose organization hierarchy
- [ ] 4.4 List skills
- [ ] 4.5 Get skill details

## 5. Knowledge API

- [ ] 5.1 Browse allowed Obsidian folders
- [ ] 5.2 Read note
- [ ] 5.3 Search knowledge
- [ ] 5.4 Protect against path escape

## 6. Model API

- [ ] 6.1 LM Studio health endpoint
- [ ] 6.2 List LM Studio models
- [ ] 6.3 Expose provider availability
- [ ] 6.4 Expose routing configuration

## 7. Frontend Foundation

- [ ] 7.1 Create React + TypeScript + Vite application
- [ ] 7.2 Add application layout/navigation
- [ ] 7.3 Add typed API client
- [ ] 7.4 Add shared loading/error states

## 8. Frontend Screens

- [ ] 8.1 Dashboard
- [ ] 8.2 Workflow catalog
- [ ] 8.3 Workflow run detail
- [ ] 8.4 Approval inbox
- [ ] 8.5 Agents / organization
- [ ] 8.6 Skills
- [ ] 8.7 Knowledge browser
- [ ] 8.8 Models
- [ ] 8.9 Settings

## 9. Local Operations

- [ ] 9.1 Add local backend start script
- [ ] 9.2 Add local frontend start script
- [ ] 9.3 Add combined Windows local launcher
- [ ] 9.4 Document LM Studio startup dependency
- [ ] 9.5 Document Obsidian vault dependency

## 10. Tests

- [ ] 10.1 Backend API tests
- [ ] 10.2 Repository persistence tests
- [ ] 10.3 Workflow start/resume tests
- [ ] 10.4 Approval API tests
- [ ] 10.5 Knowledge path security tests
- [ ] 10.6 Frontend component tests
- [ ] 10.7 End-to-end local smoke test

## 11. Validation

- [ ] 11.1 Validate OpenSpec
- [ ] 11.2 Run full backend tests
- [ ] 11.3 Run frontend tests
- [ ] 11.4 Demonstrate local application startup
- [ ] 11.5 Start an existing business workflow from UI
- [ ] 11.6 Complete a founder approval from UI
