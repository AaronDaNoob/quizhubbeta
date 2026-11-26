# Quiz Hub

Quiz Hub is a focused, browser-based study tool built with plain HTML, CSS, and JavaScript. It is designed to feel quick and uncluttered: choose a quiz, work through the questions, and use the built-in results to see where you stand.

## Features

- Responsive layout for phones, tablets, and desktop screens
- Light and dark themes with saved preference
- Sidebar navigation with collapsible layout
- Filters by subject and unit
- Quiz cards showing subject, unit, and question count
- Optional question and option shuffling
- Progress percentage and question tracking
- Countdown-free timer display for each attempt
- Keyboard controls for moving between questions and selecting options
- Previous and next navigation
- Answer selection with immediate visual state
- Reveal-answer mode with explanations when available
- Completion screen with score, correct-answer count, and time taken
- Performance dashboard grouped by subject
- Review tab for revisiting saved attempts and individual answers
- Local browser storage for settings, timers, and quiz attempts
- Mobile swipe gesture for closing the sidebar
- Discord link for reporting errors and requesting additions
- No framework, build tool, package installation, or backend required

## Tags and quiz metadata

The quiz interface supports metadata-driven organization, including subjects, units, categories, difficulty levels, cycles, descriptions, versions, and tags. The current data uses tags such as `iks`, `indian-knowledge-system`, `unit-3`, `literature`, `languages`, `ethics`, `art-and-architecture`, `folk-art`, and `performing-arts`.

Questions also carry their own IDs, categories, difficulty values, and tags, making the bank straightforward to extend or connect to another loader later.

## Run locally

Serve the repository from a local web server so browser scripts load correctly:

```bash
python -m http.server 8000
```

Then open [http://localhost:8000](http://localhost:8000) in a browser.

## Project structure

```text
index.html        Main application and interface logic
iks-unit3.js     Quiz data and metadata
discord-logo.svg  Discord invite icon
```

## Editing quiz data

Quiz records are plain JavaScript objects. A quiz contains identifying metadata and a `questions` array. Each question includes its text, four options, a zero-based `correct` index, and per-question metadata.

## Deployment

The project is static and can be deployed directly to GitHub Pages, Vercel, Netlify, or any host that serves HTML, CSS, JavaScript, and assets.
