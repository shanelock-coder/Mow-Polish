# Mów — Polish conversation trainer

## Intended result
A working, phone-friendly web app inspired by the supplied dark conversational-trainer screenshot, not a static mock-up. Three core modes: flip/hear/self-rate flashcards, due-first spaced repetition, and multiple-choice or typed quizzes. English interface, Polish learning content. Beginner-first, practical conversation, with brief explanations and a few Croatian comparisons relevant to the learner.

## Delivery and architecture
No build dependencies at runtime, accounts, tracking, paid APIs, or backend. Separate authored data, pure study engine, UI controller, and CSS; a small build script produces one directly openable HTML file and an optional static-host/PWA bundle. Progress belongs to this browser and can be exported/imported as JSON. Device speech synthesis uses actual available Polish voices only; absence is reported, never replaced silently by an English voice. Hosting is not assumed or fabricated.

## Experience
Responsive dark charcoal workspace with warm gold accents, an uncluttered dashboard, 16 topic decks of 20 cards each, local progress, a daily goal, activity and achievements, saved cards, a searchable phrasebook, custom cards, settings, and a sound guide. Clear informal/formal and speaker-gender notes; no pronunciation recognition or unearned fluency claims. Card forms follow an editable masculine/feminine speaker setting. Polish diacritics can be strict or lenient in typed recall. Untimed rounds support 10/20/30/40 cards.

## Correctness
Answers save immediately. Spacing advances only when due; extra early practice does not manufacture mastery. Again schedules a short retry; due cards come before unseen cards. Zero stats for a new learner, no sample/fake activity. Validate imports and escape user text. Gracefully handle storage and speech being unavailable. Modal keyboard support, visible focus, no mobile horizontal overflow.

## Verification
Node unit tests for data, scheduling, normalization, import validation, dates and quiz choices. Browser interaction tests for all modes, navigation, filtering, settings, custom cards, restore/reload and error states. Desktop/mobile visual inspection. Chromium test results do not establish actual iPhone Safari or installed-voice pronunciation quality.
