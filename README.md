# Mów — Polish conversation trainer

A complete, self-contained Polish-learning web app inspired by your dark flashcard-trainer reference. Version 1.1 — iPhone/Safari compatibility update.

## Start here

**On a computer:** open `Mow_Polish.html` in a full, modern web browser. Everything needed for the interface and lessons is inside that file; no installation, account, API key or build step is required. Keep the file in the same location and use the same browser for consistent access to your saved progress. Export a backup before moving it.

**On iPhone/iPad:** do not judge the app from the Apple Files/Quick Look preview: that viewer does not execute the lesson app. Use the hosted `index.html` in Safari. Once open in Safari, use **Share → Add to Home Screen** for app-style launch and offline caching after the first successful load.

**As a website, including on your phone:** publish `index.html`, `manifest.webmanifest`, `sw.js`, `icon.svg`, `icon-192.png` and `icon-512.png` together in one directory on an HTTPS static web host. Open that website in your phone's browser. The bundle includes the manifest and service worker for home-screen installation and offline caching after a successful initial load. Actual installation, voice availability and caching depend on the browser. A downloaded HTML preview in a file manager or chat attachment viewer is not the same as running a hosted web app.

**This delivery is not deployed to a public website.** The website files are ready to host; there is no invented live URL. The standalone HTML does not register a service worker.

For local development on a computer with Python, run this command inside the extracted folder, then open `http://localhost:8000` in your browser:

```sh
python -m http.server 8000
```

## What is included

- **320 original cards, 16 topics:** My story; Greetings & small talk; Ask a question; Conversation lifesavers; Your everyday verbs; Around the house; Food & coffee; Shopping & money; Getting around; Family & people; Opinions & feelings; Weather & seasons; Numbers & time; Connect your thoughts; Yesterday & tomorrow; Work & free time.
- **Flashcards:** reveal the translation, play the Polish phrase, read usage notes, and grade Again / Hard / Good / Easy.
- **Drill (spaced repetition):** prioritises due reviews, then unseen cards. Previously studied cards that are not due are excluded from this mode.
- **Quizzes:** multiple choice or typed answers, in either English–Polish direction. Correct-answer feedback, a session summary, missed phrases, and a Polish-letter toolbar are included.
- **Your phrasebook:** search in English or Polish, filter by topic or learning stage, save favourite cards, and create/edit/delete your own phrases. Custom phrases work in all study modes.
- **Progress:** daily goal, XP, streak, weekly activity, earned achievements, and per-topic learning stages. A fresh learner starts at zero, with no fabricated activity.
- **Your settings:** first name, masculine/feminine self-description forms, optional Croatian comparisons, practice length, spelling strictness, audio rate and available Polish voice.
- **Your data:** automatic local saving, JSON backup/restore, safe reset and a warning when storage is unavailable. An unreadable existing save is preserved rather than silently overwritten.

Round sizes are 10, 20, 30 or 40 cards. A round may be shorter when a topic or due-review pool has fewer eligible cards. There are no duplicate cards within a round. Leaving early preserves answered cards and leaves unanswered cards untouched.

## A suggested first session

Choose **Greetings & small talk → Flashcards**, set a 10-card round, and use English → Polish. Say the phrase before revealing it. Use Good when you remembered it, Hard when it was a struggle, and Again when you need another look. Try a multiple-choice quiz afterwards. Drill is for returning to the words at their scheduled time, not repeating the same tiny set immediately.

“My story” includes editable-name introduction cards and practical example sentences, including being from Australia and learning Polish. These are teaching examples, not a verified biography. Other examples need not describe you personally. You can add your own alternatives to the custom deck.

## Polish and answer checking

Cards have short original usage notes. Topics include useful distinctions such as `Mam samochód` versus `Nie mam samochodu`, polite `pan/pani` forms, and the difference between a speaker's gender and the person being addressed. Some cards include an optional Croatian bridge; this is not a separate Croatian course.

Typed answers accept case and punctuation differences, common English contractions, and explicitly listed Polish alternatives. English recognition accepts short answers without teaching labels such as “informal”. Strict Polish spelling is off by default: missing marks are accepted and the proper spelling is shown. Switch it on to require Polish letters.

This is **phrase-based checking**, not an AI translation judge. Another grammatical translation may be rejected when it is not listed. The app explains this on a missed typed answer. The A1/A2 labels indicate approximate topic difficulty, not a complete certified curriculum or a claim of fluency.

## Review scheduling

New → Learning → Familiar → Remembering → Confident → Mastered.

A successful review advances one stage only when the card is due (or new). Good schedules the next review in 1, 3, 7, 14 or 30 days depending on the new stage. Easy uses 1.5 times that interval without skipping a stage. Hard keeps the current stage, with a minimum of Learning, and schedules a due card in six hours. Again reduces the stage by one, with a minimum of Learning, and schedules a review in ten minutes.

An early successful flashcard or quiz practice adds to your activity but does **not** advance the card's stage or push its due date further away. A missed early practice brings the card back sooner. “Mastered” is an app review stage, not a guarantee of language proficiency. Flashcard recap percentages are self-rated recall; quiz percentages are actual marked answers.

XP per answer: Again 2, Hard 5, Good 10, Easy 15. Quiz answers use Good or Again. Days and streaks follow the device's local calendar.

## Audio

Audio uses your browser's speech-synthesis API and actual Polish voices it exposes. It is not a collection of recorded native-speaker clips. The app refuses to substitute an English voice when no Polish voice is available. It provides an audio-help message instead.

Choose an available voice under **Settings → Hear the language**. Adding a Polish system voice and reopening the browser may help, but voice exposure varies by platform. The default rate is 0.9; the separate Slow button uses 0.65. Some voices require internet access. Speech processing is controlled by your device/browser provider and may be remote for a non-local voice. No microphone is used, and pronunciation is not scored.

## Keeping your progress

Use **Settings → Export backup** regularly and before changing browsers, moving files, clearing website data or updating your copy. Use **Import backup** in the new copy to restore it. An import replaces current learning data only after confirmation; it does not merge accounts or devices.

Storage is local to this browser and origin/file location. Browser rules for `file:` URLs, private browsing or storage restrictions differ. If a warning is shown, learning still works for the current session, but export a backup before closing it. There is no cloud synchronisation. Backups contain your first name, learning history and any personal phrases you add, so keep them private.

Reset requires typing `RESET`. It clears learning history, XP and activity but retains settings, saved phrases and custom cards. Editing a custom card resets that card's stage. Deleting a custom card removes its saved status and card-specific review history; previous overall activity remains a historical record.

## Files and development

```text
Mow_Polish.html         Standalone app: open directly on a computer
index.html             Website/PWA entry point
manifest.webmanifest   Website installation metadata
sw.js                  Website offline-cache worker
icon*.png, icon.svg    App icons (no font files)
src/data.js            320 authored cards and topic metadata
src/engine.js          Pure scheduling, grading and import-validation logic
src/app.js             Interface, interactions, speech and local persistence
src/styles.css         Responsive dark interface
src/shell.html         Build template
build.py               Inlines source into both app variants
tests/                 Node and Chromium acceptance tests
docs/                  Design notes, screenshots and verification evidence
```

Rebuild with `python build.py`. Test pure logic and content integrity with `node --test tests/*.test.cjs`. The build uses CairoSVG or Pillow to regenerate icons. These tools are development dependencies, not requirements for using the delivered app. The browser test script additionally requires Python Playwright and a compatible Chromium executable. Its current executable path is `/usr/bin/chromium`; adapt this for a different development machine.

For a hosted update, increment the service-worker cache version in `build.py`, rebuild, and replace the website files together. Back up progress before updating. Do not rename existing built-in card IDs casually: saved review history refers to those IDs.

## Verification and limits

The delivered build passed **42 Node tests** covering card integrity, answer normalisation, gender/name substitution, scheduling, date handling, quiz choices and backup validation, plus **20 Chromium acceptance checks** exercising all main UI flows. Responsive layout checks covered widths of 320, 360, 390, 430, 768, 1024 and 1440 pixels. Desktop, mobile, flashcard and quiz screenshots were inspected. No uncaught JavaScript errors occurred in the passing browser run.

The Chromium environment blocks URL navigation through administrator policy. The browser tests therefore render the actual built HTML with `set_content`, and persistence tests use an explicitly simulated localStorage boundary. These tests establish DOM interaction and rendering, **not** native `file:` storage, hosted-origin persistence, public deployment, service-worker lifecycle/offline installation, or actual iPhone/Safari behaviour. Speech configuration and unavailable-voice handling were tested; audible output and pronunciation quality were not tested on a physical device. Native file downloads were not exercised; the generated backup Blob and import flow were tested.

The service worker and manifest are included but have not been verified in an installed, hosted PWA. Version 1.1 adds iOS safe-area sizing, 16px form controls to avoid focus zoom, touch-oriented controls, Apple web-app metadata, and a visible Quick Look fallback instead of a blank shell when JavaScript is not executed. No external user account or hosting project has been created.

## References

The interface, cards and notes are original. Grammar checks consulted Oscar E. Swan's *A Grammar of Contemporary Polish*. No textbook passages, third-party voice recordings, or proprietary fonts are bundled.

- Grammar: https://lektorek.org/lektorek/grammar.pdf
- Device voices: https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis/getVoices
- Browser storage, including `file:` behaviour: https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage
- Service workers and secure hosting: https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API/Using_Service_Workers

Original application code and authored cards are supplied under the included MIT licence. Linked reference works retain their own rights.
