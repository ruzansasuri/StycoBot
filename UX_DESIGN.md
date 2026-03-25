# Career Chatbot — UX Design Document
**Version:** 1.0
**Status:** In progress
**Last updated:** March 2026

---

## Overview

A portfolio chatbot embedded in a personal site that lets visitors query a career history through natural conversation. The bot is trained on three career documents and responds via a public LLM. The UI is hosted on GitHub Pages and communicates with two AWS Lambda functions via API Gateway.

The design is split into two patch tracks: **Current** (v1 scope) and **Future** (subsequent patches).

---

## Users

**Primary:** Recruiters, hiring managers, and collaborators visiting the portfolio who want to quickly understand the owner's background without reading a CV.

**Secondary:** The developer themselves, who needs a private admin interface to manage docs (future scope).

---

## Current — v1 Scope

### 1. Header

- Displays the owner's name and title
- A **Download CV** button is always visible in the top-right corner
  - Calls `get_cv_download_url()` on Lambda A
  - Returns a presigned S3 URL — triggers a direct browser download
  - No login or gate required

---

### 2. Suggested prompts

- Shown on initial load, before the user has typed anything
- Populated by calling `get_suggested_questions()` on Lambda A at page load
- Displayed as tappable chips below the message thread
- Chips are hardcoded on the Lambda — no AI call required, fast response
- Selecting a chip populates the input and sends immediately
- Prompt section fades or collapses once the user has sent their first message

**Example prompts:**
- What stack does Ruzan work with?
- Most impactful projects?
- Is Ruzan open to new roles?
- How does Ruzan approach system design?

---

### 3. Chat — send and receive

- User types a message (max 300 characters) and sends via button or `Enter`
- Message is appended to the thread immediately as a user bubble
- A typing indicator (three animated dots) appears while awaiting the Lambda response
- On response, the typing indicator is replaced with the bot reply bubble
- Input clears after send

**Lambda B call — `ask_career_bot(question, history)`**

| Parameter | Type | Description |
|---|---|---|
| `question` | `string` | The user's current message |
| `history` | `message[]` | Full conversation history for the session |

Response is a plain string rendered as the bot's reply.

---

### 4. Session context

- Conversation history is stored in browser memory (not persisted to a database)
- The full history is sent with every request to Lambda B
- Lambda B prepends career docs as a system prompt and passes history + question to OpenAI
- Lambda remains stateless — all state lives in the browser
- History is cleared on page refresh

---

## Future Patches

### Reconnecting state *(patch 2)*
When the user has been idle for 4+ minutes, the send button changes to a `reconnecting...` state. This is a client-side timer — no AWS call needed. The button returns to normal once the next response arrives. Communicates to the user that the first response after idle may be slower without exposing infrastructure details.

### Admin panel *(patch 3)*
A secret route (not linked from portfolio navigation) where the developer can view and update the career documents that are injected into the Lambda system prompt. Access controlled, not publicly discoverable.

### Metrics *(patch 4)*
Intentionally vague at this stage. Likely session counts, common questions asked, and response quality signals.

### Stronger persistence *(patch 5)*
Intentionally vague at this stage. May involve cross-session history, user identification, or a database layer.

---

## MCP Tool Surface

All tools are exposed via Lambda A or Lambda B through API Gateway. The UI calls tools directly over HTTPS — there is no separate MCP runtime process.

| Tool | Lambda | Called when |
|---|---|---|
| `get_suggested_questions()` | A | Page load |
| `get_cv_download_url()` | A | User clicks Download CV |
| `ask_career_bot(question, history)` | B | User sends a message |

---

## Infrastructure Summary

| Component | Role | Cost |
|---|---|---|
| GitHub Pages | Hosts React UI | Free |
| API Gateway | HTTPS entry point, IP rate limiting | Free tier |
| Lambda A | Lightweight tools — no OpenAI | Free tier |
| Lambda B | Chat — calls OpenAI | Free tier |
| S3 | Stores CV PDF, presigned URL access | ~$0 |
| OpenAI `gpt-4o-mini` | Language model | ~$0.01–0.05/mo |
| EventBridge (CloudWatch) | Pings Lambda B every 4 min to keep warm | Free tier |

**Fixed monthly cost: $0. Variable cost: OpenAI tokens only.**

---

## Open Questions

- [ ] Confirm final copy for suggested prompts once career docs are finalised
- [ ] Decide on max history length before truncation (currently: full session, cap TBD)
- [ ] Agree on CV file name and S3 bucket structure before Lambda A is built
- [ ] Define the secret admin route path