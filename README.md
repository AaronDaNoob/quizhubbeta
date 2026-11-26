# Quiz Hub

A clean, fast quiz workspace for revision, practice, and self-checking. Quiz Hub runs in the browser with no framework or build pipeline, keeping the experience simple to launch and easy to maintain.

## Features

- Responsive interface for phones, tablets, and desktop screens
- Light and dark themes with saved preference
- Collapsible sidebar navigation
- Subject and unit filtering
- Quiz cards with category, unit, and question-count details
- Optional question and option shuffling
- Progress percentage and question tracking
- Per-attempt timer
- Keyboard navigation with arrow keys and Enter
- Previous and next question controls
- Selected, correct, and incorrect answer states
- Reveal-answer mode with optional explanations
- Completion screen with score, correct answers, and time taken
- Performance dashboard grouped by subject
- Review mode for saved attempts and individual answers
- Local browser storage for settings and quiz history
- Mobile swipe gesture for closing the sidebar
- Dynamic visit counter through a protected Vercel endpoint
- Discord contact link for corrections and quiz requests
- No framework, package installation, or build step

## Quiz organization

Quiz content is organized with metadata rather than hard-coded navigation. Records can include:

- Subjects and units
- Categories and cycles
- Difficulty levels
- Descriptions and versions
- Quiz-level and question-level IDs
- Searchable tags

The current tag set covers areas such as chemistry, biology, mathematics, environmental studies, human values, engineering, Kannada, social and cultural studies, Indian Knowledge System, literature, languages, ethics, architecture, folk art, and performing arts.

## Visit counter

The displayed visit total is updated through `/api/visits` when deployed on Vercel. The counter starts from the existing 13,900 visits and increments from there. The endpoint uses a server-side counter and a short-lived hashed visitor key to avoid counting repeated refreshes from the same visitor throughout the day. It does not expose credentials or accept arbitrary counter values from the browser. If the service is unavailable, the interface keeps the 13,900 baseline instead of showing an empty value or interrupting the quiz.

## Run locally

Serve the repository from a local web server so browser scripts load correctly:

```bash
python -m http.server 8000
```

Then open [http://localhost:8000](http://localhost:8000) in a browser.

The visit counter requires Vercel KV environment variables when deployed. The rest of the application works locally without any dependencies.

## Project structure

```text
index.html        Main application and interface logic
iks-unit3.js     Quiz data and metadata
api/visits.js     Protected visit-counter endpoint
discord-logo.svg  Discord invite icon
```

## Editing quiz data

Quiz records are plain JavaScript objects. Each question includes its text, four options, a zero-based `correct` index, and optional metadata such as an ID, category, difficulty, and tags.

## Deployment

The application can be deployed to Vercel, GitHub Pages, Netlify, or another static host. The dynamic visit counter is available on Vercel when the project is connected to Vercel KV; static hosts will continue to serve the quiz without that endpoint.
