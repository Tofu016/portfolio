# Cristopher Pondoc: Portfolio

A pixel-art airport portfolio, loosely inspired by the interior of NAIA Terminal 3: a departures board on the main page leads to three gates.

Built with plain HTML, CSS and JavaScript, so there is no build step. Open `index.html` or serve the folder with any static server.

- `index.html`: main page (about, departures board, contact)
- `developer.html`: gate D1 (full-stack developer), projects, tech stack, certifications
- `photography.html`: gate P2, landscape gallery, editing software
- `pilot.html`: gate A3, crew card, spotting log, flight sim, flight training
- `assets/css/site.css`: shared styles
- `assets/js/board.js`: split-flap departures board and clock
- `assets/js/gallery.js`: photo viewer
- `images/web/`: web-sized copies of the nature photos
- `images/pixel/`: pixel-art scenes and sprites
- `tools/pixel/scenes.py`: generates `images/pixel/` (needs Pillow). Edit it, then run `python tools/pixel/scenes.py` from the repo root.

Placeholders to fill in are marked with `PLACEHOLDER` comments in the HTML.
