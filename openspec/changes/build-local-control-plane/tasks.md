# Tasks

## 1. Backend Foundation

- [x] 1.1 Add FastAPI application
- [x] 1.2 Add API configuration and startup health checks
- [x] 1.3 Add CORS/local frontend configuration
- [x] 1.4 Add structured API error handling

## 2. Runtime Persistence

- [x] 2.1 Define runtime repository interfaces
- [x] 2.2 Add SQLite local database
- [x] 2.3 Persist workflow run metadata
- [x] 2.4 Persist approval requests
- [x] 2.5 Persist runtime events
- [x] 2.6 Persist idempotency records
- [x] 2.7 Keep PostgreSQL migration boundary explicit

## 3. Workflow API

- [x] 3.1 List available workflows
- [x] 3.2 Start workflow
- [x] 3.3 Get workflow run
- [x] 3.4 List workflow runs
- [x] 3.5 Resume approval interrupt
- [x] 3.6 Resume error recovery
- [x] 3.7 Stream workflow state/events

## 4. Organization API

- [x] 4.1 List agents
- [x] 4.2 Get agent details
- [x] 4.3 Expose organization hierarchy
- [x] 4.4 List skills
- [x] 4.5 Get skill details

## 5. Knowledge API

- [x] 5.1 Browse allowed Obsidian folders
- [x] 5.2 Read note
- [x] 5.3 Search knowledge
- [x] 5.4 Protect against path escape

## 6. Model API

- [x] 6.1 LM Studio health endpoint
- [x] 6.2 List LM Studio models
- [x] 6.3 Expose provider availability
- [x] 6.4 Expose routing configuration

## 7. Frontend Foundation

- [x] 7.1 Create React + TypeScript + Vite application
- [x] 7.2 Add application layout/navigation
- [x] 7.3 Add typed API client
- [x] 7.4 Add shared loading/error states

## 8. Frontend Screens

- [x] 8.1 Dashboard
- [x] 8.2 Workflow catalog
- [x] 8.3 Workflow run detail
- [x] 8.4 Approval inbox
- [x] 8.5 Agents / organization
- [x] 8.6 Skills
- [x] 8.7 Knowledge browser
- [x] 8.8 Models
- [x] 8.9 Settings

## 9. Local Operations

- [x] 9.1 Add local backend start script
- [x] 9.2 Add local frontend start script
- [x] 9.3 Add combined Windows local launcher
- [x] 9.4 Document LM Studio startup dependency
- [x] 9.5 Document Obsidian vault dependency

## 10. Tests

- [x] 10.1 Backend API tests
- [x] 10.2 Repository persistence tests
- [x] 10.3 Workflow start/resume tests
- [x] 10.4 Approval API tests
- [x] 10.5 Knowledge path security tests
- [x] 10.6 Frontend component tests
- [x] 10.7 End-to-end local smoke test

## 11. Validation

- [x] 11.1 Validate OpenSpec
- [x] 11.2 Run full backend tests
- [x] 11.3 Run frontend tests
- [x] 11.4 Demonstrate local application startup
- [x] 11.5 Start an existing business workflow from UI
- [x] 11.6 Complete a founder approval from UI

Verification evidence: `docs/ImplementationVerification.md`. Remote CI has not run; local checks passed.
