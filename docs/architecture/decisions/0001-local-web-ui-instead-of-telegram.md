# 0001. Local web UI instead of Telegram for the MVP

- **Status:** Accepted
- **Date:** 2026-10-04

## Context

The MVP draft used Telegram as the whole interface: brief as a message, inline 👍/👎 buttons, `/stats` command. I prefer a local application with its own backend and frontend, and don't want to depend on Telegram.

## Options considered

1. **Telegram bot:** free push notifications and mobile access, almost no UI work. But depends on Telegram, and card pages can't be served from localhost to a phone.
2. **Local web app (backend + frontend):** full control, a base for the v1 dashboard. No push: I have to open it myself.

## Decision

Build a local web app. The brief is the Today page; ratings are buttons on it; stats is a page.

## Consequences

- No push, so "I open the brief" is measured by `briefs.opened_at`, set on first view.
- No mobile access while it runs only on my laptop.
- The four MVP pages become the first pages of the v1 dashboard.
- A Windows toast notification at brief time is an optional later add-on.
