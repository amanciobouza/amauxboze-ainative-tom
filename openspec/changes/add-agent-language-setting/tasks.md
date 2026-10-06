# Tasks

- [x] 1. Specify authorized scope and migration behavior.
- [x] 2. Add validated persisted setting and provider-neutral language instructions.
- [x] 3. Add German/English selector and document behavior.
- [x] 4. Verify defaults, persistence, invalid codes, all provider requests, frontend build and OpenSpec.

Evidence: 113 backend tests passed, 3 frontend tests passed, TypeScript/Vite production build and OpenSpec validation passed. Provider request tests cover German/English for all three providers; API tests cover legacy defaults, invalid codes and restart persistence. Running local settings explicitly saved as de.
