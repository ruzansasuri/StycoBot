# Career Chatbot — Phases of Change
**Version:** 1.0
**Status:** In progress
**Last updated:** March 2026

---

## Context

This document tracks the incremental changes required to evolve the existing career chatbot into the architecture defined in `system-design.md` and `ux-design.md`. Each phase is independently deployable and leaves the system in a working state.

### On RAG vs plain text injection

The existing system uses RAG (embeddings + vector retrieval) to pass career context to the LLM. This is being dropped. The career docs total approximately 1,800 tokens — well below the threshold where RAG adds value. Plain text injection into the system prompt is simpler, cheaper, and more reliable at this scale. RAG would only be warranted with 20+ documents.

S3 is used in this project solely to store and serve the CV PDF for download. It is not a vector store.

---

## Phase 1 — Build Lambda A + S3 bucket

**Goal:** Stand up the new lightweight Lambda and the S3 bucket for CV storage. No UI changes yet.

### Tasks

**S3**
- [ ] Create a private S3 bucket for CV storage
- [ ] Upload CV PDF to the bucket
- [ ] Confirm bucket policy blocks all public access

**Lambda A — new function**
- [ ] Create a new Python Lambda function separate from the existing chat Lambda
- [ ] Implement `get_suggested_questions()` — returns a hardcoded list of prompt strings drawn from the career docs
- [ ] Implement `get_cv_download_url()` — generates a presigned S3 URL with a short expiry (e.g. 5 minutes)
- [ ] Add IAM permission for Lambda A to call `s3:GetObject` on the CV bucket
- [ ] Wire Lambda A to API Gateway — new route, separate from existing chat route
- [ ] Test both tools via API Gateway URL directly (curl or Postman)

### Decisions required before starting
- Confirm CV file name and S3 bucket name
- Confirm the final list of suggested questions (dependent on career docs content)
- Confirm presigned URL expiry time

### Notes
- Lambda A has no OpenAI dependency — keep the deployment package minimal
- Lambda A does not receive or store any conversation history

---

## Phase 2 — Update UI and integrate Lambda A

**Goal:** Replace the existing UI with the new design and wire up Lambda A tools. Lambda B (chat) is untouched in this phase.

### Tasks

**UI**
- [ ] Implement new chat UI design (per `ux-design.md`)
- [ ] On page load, call `get_suggested_questions()` and render chips
- [ ] Implement chip tap — populates input and sends immediately
- [ ] Collapse/fade prompt chips after first user message
- [ ] Implement Download CV button — calls `get_cv_download_url()` and triggers browser download
- [ ] Implement typing indicator while awaiting bot response
- [ ] Implement character counter on input (max 300)
- [ ] Deploy updated UI to GitHub Pages

### Notes
- The existing Lambda B chat endpoint remains unchanged — the UI still calls it the same way as before
- Session history continues to work as it does today — no changes to history logic yet

---

## Phase 3 — Token and session limits

**Goal:** Add guardrails to prevent runaway token usage. Changes are entirely in Lambda B.

### Tasks

- [ ] Define token cap per session (recommended starting point: 8,000 input tokens)
- [ ] Define message cap per session (recommended starting point: 20 messages)
- [ ] Add token counting in Lambda B before each OpenAI call — count system prompt tokens + history tokens + current message tokens
- [ ] If token cap is exceeded, return a capped response to the UI (e.g. "This session has reached its limit. Please refresh to start a new conversation.")
- [ ] If message cap is exceeded, return the same capped response
- [ ] Add history truncation — if history exceeds N messages, drop the oldest pairs first (keep system prompt intact)
- [ ] Test at limit boundaries

### Decisions required before starting
- Confirm token cap value
- Confirm message cap value
- Confirm copy for the session-limit message shown to users

### Notes
- Token counting should use `tiktoken` (OpenAI's tokeniser library) for accuracy
- Truncation should always preserve the system prompt — only history is trimmed
- These limits exist to protect cost, not UX — set them generously enough that normal conversations never hit them

---

## Phase 4 — Migrate Lambda B to plain text injection + message history

**Goal:** Remove RAG entirely. Replace embeddings-based context with plain text injection. Add structured message history and exact prompt passthrough for suggested questions.

### Tasks

- [ ] Load all three career docs as plain text strings at Lambda B startup (not per-request)
- [ ] Construct system prompt as: career docs concatenated with a brief instruction header
- [ ] Remove all embeddings and vector retrieval code from Lambda B
- [ ] Remove OpenAI embeddings API calls
- [ ] Update Lambda B handler to accept `history` parameter (array of `{role, content}` objects)
- [ ] Pass `history` as the conversation history in the OpenAI messages array
- [ ] Update API Gateway request schema to include `history` field
- [ ] Update UI to maintain history in browser state and pass it with each request
- [ ] Verify suggested question chips send the exact prompt string (not a paraphrase)
- [ ] Remove any Lambda dependencies that were only used for RAG (e.g. vector DB client)
- [ ] Test a multi-turn conversation end to end

### Decisions required before starting
- Confirm final plain text content of all three career docs
- Confirm system prompt instruction header copy

### Notes
- Career docs are loaded once when the Lambda container initialises, not on every invocation — this is efficient and requires no caching logic
- This phase makes the system cheaper and simpler — the OpenAI embeddings API call disappears entirely
- History format must match OpenAI's messages array: `[{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]`

---

## Phase 5 — Warm start features

**Goal:** Minimise cold start impact on Lambda B and surface it gracefully in the UI where unavoidable.

### Tasks

**EventBridge keep-warm ping**
- [ ] Create an EventBridge rule that invokes Lambda B every 4 minutes
- [ ] Add warmup detection in Lambda B handler — if `event.source == "warmup"`, return immediately without calling OpenAI
- [ ] Test that the ping correctly exits early and does not consume tokens

**UI — reconnecting state**
- [ ] Track timestamp of last sent message in browser state
- [ ] If time since last message exceeds 4 minutes, change send button to `reconnecting...` state
- [ ] Return button to normal state once the next response arrives
- [ ] No AWS calls required — this is a client-side timer only

### Notes
- The 4-minute ping interval is intentionally conservative — it sits below the AWS idle timeout floor of ~5 minutes
- The reconnecting UI state is cosmetic — it does not retry the request or add any network logic
- These two changes are independent and can be deployed separately if needed

---

## Phase Summary

| Phase | Touches | Deliverable |
|---|---|---|
| 1 | Lambda A (new), S3 (new), API Gateway | Lambda A live, CV downloadable via presigned URL |
| 2 | UI only | New UI live on GitHub Pages, Lambda A integrated |
| 3 | Lambda B only | Token + message caps enforced |
| 4 | Lambda B, UI | RAG removed, plain text injection, history wired end to end |
| 5 | Lambda B, UI, EventBridge | Warm pings active, reconnecting state in UI |