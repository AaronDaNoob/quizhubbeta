# Quiz Hub

Quiz Hub is a lightweight browser-based quiz application for students who want a simple way to revise course material. It runs as a static site, so there is no build step, database, or account system to configure.

## What it includes

- Clean quiz interface with progress tracking and answer review
- Light and dark themes
- Subject and unit filters
- Question randomization and optional timers
- Performance and review views
- Indian Knowledge System (IKS) Unit 3 with 90 questions covering literature, languages, ethics, architecture, folk traditions, dance, music, and theatre
- Responsive layout for desktop and mobile screens

## Run locally

Serve the repository from a local web server so browser scripts load correctly:

```bash
python -m http.server 8000
```

Open [http://localhost:8000](http://localhost:8000) in a browser.

## Project structure

```text
index.html      Main application
iks-unit3.js   IKS Unit 3 question bank
discord-logo.svg  Discord invite icon
```

The project uses plain HTML, CSS, and JavaScript. Quiz content is kept close to the application so it can be edited without a framework or dependency installation.

## Adding questions

The IKS Unit 3 bank is defined in `iks-unit3.js`. Each question contains its text, four options, and a zero-based correct answer index. The current Unit 3 set intentionally keeps the first option as the answer for every question.

## Deployment

Because the app is static, it can be deployed directly to GitHub Pages, Vercel, Netlify, or any hosting service that serves HTML files.
