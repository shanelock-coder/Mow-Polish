# Mów implementation plan

**Goal:** Deliver a standalone Polish-learning web app matching the reference's dark flashcard/SRS/quiz workflow.
**Architecture:** Data and pure engine feed a DOM UI; a build step inlines all runtime code. Optional static hosting adds a manifest and service worker.
**Tech:** HTML, CSS, plain JavaScript, Node test runner, Python build and Playwright verification.
**Spec:** DESIGN.md

1. [x] Write tests for normalized recall, due-aware stage progression, deck selection, unique choices, activity, import validation and 320-card integrity. Run red.
2. [x] Author 16 curated topic decks and implement the pure engine. Run all unit tests.
3. [x] Write browser acceptance tests. Implement responsive dashboard, phrasebook, sound guide, progress, modal setup, flashcards, drill, quiz, recap, settings, backups, and custom cards.
4. [x] Build standalone and static-host variants. Run browser tests including storage failures, mobile interaction. Native URL opening and installed offline/PWA behaviour could not be exercised under the environment’s navigation policy; see README verification limits.
5. [x] Inspect desktop and mobile screenshots, reconcile defects, rerun all tests, and package README and test evidence.

## Review focus
- Early repeated practice must not inflate mastery or defer a review.
- Backups may contain invalid types, large payloads, missing fields, prototype keys or HTML.
- A device may expose zero Polish voices or block local storage.
- Search and topic filters may produce an empty set; saved cards may be absent.
- Small screens, long Polish sentences and dialogue focus must remain usable.

## Actual validation scope
42 Node tests and 20 Chromium DOM acceptance checks. Storage reload tests use an explicit in-memory platform boundary. Device audio, Safari, native file downloads and installed service-worker behaviour remain unverified.
