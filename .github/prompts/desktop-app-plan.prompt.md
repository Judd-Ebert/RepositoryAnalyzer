# Desktop-First MVP Plan

Date: 2026-04-28

## Decisions Locked
1. Python/runtime delivery for MVP: require local Python install (simpler release path, expected audience likely already has it).
2. Query scope for MVP: single repository at a time.
3. Runtime scope for MVP: support both local model runtime and API runtime.
4. Timeline preference: balanced 4-6 week build.

## Recommendation for macOS Distribution
For the fastest MVP, ship unsigned developer/test builds first, then add signing/notarization before broader public distribution.

Why:
- Unsigned builds reduce release friction while core UX/API are still changing.
- Signing/notarization is important for trust and install experience, but is usually better after MVP behavior stabilizes.
- This keeps effort focused on product correctness and local model performance first.

## Target Architecture
1. Desktop shell: Tauri.
2. Frontend: React + TypeScript + Vite.
3. Backend: existing FastAPI service, started and monitored by desktop shell.
4. Transport: localhost HTTP.
5. Streaming: keep current chunked streaming for MVP (upgrade to SSE only if structured events are required).

## Phase Plan

### Phase 1 - Desktop Bootstrap and Process Lifecycle
Deliverables:
- Tauri + React/Vite project scaffold.
- App startup that launches backend process.
- Health check gating before UI enables ingest/query actions.

Acceptance criteria:
- Desktop app launches on Windows and macOS dev machines.
- Backend starts from desktop app and health endpoint responds.
- App shutdown cleans backend process.

### Phase 2 - Backend Contract Hardening
Deliverables:
- Add CORS/localhost-safe configuration.
- Refactor ingest input so full URLs are not passed as path segments.
- Add ingestion status endpoint (started/running/success/failure).

Acceptance criteria:
- Ingest endpoint works with normal GitHub URLs safely.
- UI can poll or subscribe to ingest status.
- Existing query endpoint continues to stream responses.

### Phase 3 - Core Desktop UI Workflows
Deliverables:
- Ingest view (repo input, start action, progress state).
- Repo selection (single-repo MVP).
- Query workspace with streaming answer panel and source snippets.

Acceptance criteria:
- User can ingest one repo and ask a question end-to-end.
- Answer appears incrementally while model generates.
- Error and empty-result states are clear.

### Phase 4 - Runtime Modes and Settings
Deliverables:
- Settings for local runtime and API runtime.
- Provider abstraction and runtime switcher in UI.
- Validation for required values (endpoint, model name, API key where needed).

Acceptance criteria:
- Both local and API modes can answer queries.
- Switching mode does not require restarting app.
- Invalid settings are surfaced with actionable messages.

### Phase 5 - Performance and Reliability Pass
Deliverables:
- Reduce rerender churn during stream updates.
- Add cancellation/retry for long running query/ingest operations.
- Add basic logs panel or diagnostics export.

Acceptance criteria:
- UI remains responsive during long responses.
- Cancel/retry behavior works consistently.
- Troubleshooting information is accessible.

### Phase 6 - Packaging and Release
Deliverables:
- Windows build artifacts and installation docs.
- macOS unsigned artifact for MVP testing.
- Signing/notarization checklist and follow-up release task.

Acceptance criteria:
- Fresh machine can run app following setup steps.
- Required Python install workflow is documented and verified.
- Release notes document known limits and next milestones.

## 4-6 Week Execution Outline
1. Week 1: Phase 1 complete; begin Phase 2 API cleanup.
2. Week 2: Finish Phase 2; start core UI in Phase 3.
3. Week 3: Finish Phase 3; begin Phase 4 runtime settings.
4. Week 4: Complete Phase 4; start Phase 5 reliability/performance.
5. Week 5: Phase 6 packaging baseline and cross-platform smoke tests.
6. Week 6: Buffer for bug fixes, docs, and first MVP release.

## Risks and Mitigations
1. Python environment mismatch on user machines.
- Mitigation: startup preflight checks and a one-command setup script.

2. Local model variability across hardware.
- Mitigation: defaults for smaller models, runtime warnings for low resources.

3. Desktop process lifecycle edge cases.
- Mitigation: explicit backend health checks, restart policy, and clean shutdown handling.

4. macOS Gatekeeper friction.
- Mitigation: keep unsigned builds for early testers only, then prioritize signing/notarization for public release.

## Verification Matrix
1. Windows dev machine: clean setup, ingest, stream query, close/reopen app.
2. macOS dev machine: same flow with unsigned MVP build.
3. Local runtime mode: model produces streamed output.
4. API runtime mode: streamed output and error handling verified.
5. Large repo ingest: progress remains visible and app stays responsive.

## Immediate Next Actions
1. Implement Phase 2 backend contract changes (CORS, ingest input shape, ingest status endpoint).
2. Scaffold frontend/desktop shell and wire health check.
3. Build streaming query UI path against existing query endpoint.
