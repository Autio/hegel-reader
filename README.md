# Hegel Reader — The Science of Logic

A day-by-day, spiraling-up commentary on Hegel's *Science of Logic*.

**[View the live page →](https://YOUR_USERNAME.github.io/hegel-reader/)**

## How it works

An AI agent reads one subsection of Hegel's *Science of Logic* each day, produces:
- Deep analytical commentary
- A growing system map
- Coherence evaluations
- Tweet-sized wisdom condensations
- Modern-world rethinkings
- Research project ideas

Everything accumulates in `commentary.md` and is rendered as a beautiful navigable HTML page at `index.html`.

## Files

| File | Purpose |
|------|---------|
| `index.html` | The rendered web page (self-contained, open in browser) |
| `commentary.md` | Running commentary (source of truth) |
| `reading_units.json` | Extracted text units from the Cambridge translation |
| `state.json` | Reading progress tracker |
| `regen_html.py` | HTML regenerator script |

## Setup

Powered by [Hermes Agent](https://github.com/NousResearch/hermes-agent) with a daily cron job.
