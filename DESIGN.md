# DESIGN.md — Nadia Fitness Dance Studio (v4)

v4 consolidates three earlier versions. Every rule below exists because something went wrong (or right) in v1–v3; the reason is written next to it. Keep this file under two pages.

## What the site is for

A parent or an adult in Torrox Costa wants to **find a class that fits who it is for and when they are free, then phone (or WhatsApp) to reserve a place.** Booking is by phone, so the phone number is the main call to action everywhere.

Home order (tested): hero + "Hoy en el estudio" → 01 Clases → 02 Horario → 03 Nadia → 04 Apúntate (steps + phone). *Why:* practical info first, trust (Nadia, 5,0 ★) right before the decision.

## Direction

**A dance-school programme with the brand's energy.** Paper and ink, numbered sections, ruled lists (v2 — the version reviewers liked most: "el 2º es mejor como página"), plus the logo's pink used boldly in a few places and photos in colour (v1's energy, which "es lo que le gusta a la gente").

Signature elements: the live **"Hoy en el estudio"** board (today's real classes, now/next) and the **pink phone block** (the one big pink area per page).

## Tokens

| | Light | Dark | Notes |
|---|---|---|---|
| `--paper` | `#F4EFE8` | `#17130F` | never pure black/white (v1's `#050505` "quemaba los ojos") |
| `--ink` | `#16120F` | `#F3EEE6` | 16:1 |
| `--muted` | `#5E554D` | `#A89E93` | ≥ 6.4:1 |
| `--rule` | `#D9D1C5` | `#3A322C` | decorative only |
| `--pink` | `#C2006A` | `#FF5AA8` | fills, big type; white on it 6.0:1 / ink on it 6.4:1 |
| `--pink-text` | `#AE005E` | `#FF5AA8` | small pink text 6.2:1 |
| `--band` | `#16120F` | `#16120F` | header is always dark: the logo is drawn for black |

Type: **Barlow Condensed 800** for display (the brand's condensed sport type), italic only for one accent word per heading; **Instrument Sans** for text (17px/1.6, ≤ 65ch).

## Rules (each one learnt the hard way)

1. **No glows, gradients, halos or neon shadows.** v1 felt "busy" and "AI-made" because of them.
2. **One filled pink element per area.** In v1 nobody could tell "qué es botón y qué no". Labels look like text, buttons look like buttons, only real buttons are filled.
3. **No small uppercase labels above headings** and no pill above the hero — an "AI" tell. Section numbers (01–04) are fine: they are the programme's structure.
4. **Display line-height ≥ 1.05** on anything that can wrap. Spanish capitals carry accents (JÓVENES, MIÉRCOLES, ¿) and at 0.9 they collide with the line above.
5. **Photos in colour.** A grayscale portrait next to a big name "da vibes de que ya está con San Pedro".
6. **No minors in photos without written consent.** Crop above the audience; never commit the originals.
7. **Never invent content**: no prices, ages, testimonials, stats, or a "free trial" ("Ven a probar" implied one — use "Contacta").
8. **Grids must fill their rows.** 7 classes = 4 dance + 3 fitness, so they are two lists, not a 4+3 grid with a hole.
9. **Baile vs fitness never by colour alone**: dance = filled dot / solid rule, fitness = ring / dashed rule.
10. **Links inside text are underlined.** Colour alone is not enough (WCAG 1.4.1).
11. **Reserve space for fixed bars**: `scroll-padding` top (sticky header) and bottom (mobile call bar) so focus is never hidden (WCAG 2.4.11).
12. **Grid columns are `minmax(0, 1fr)`**, never bare `1fr`: a no-wrap row inside a `1fr` column made v2 overflow 590px on phones.
13. **Content works without JavaScript.** Pages are static HTML generated from one data file; JS only adds filters, tabs, the "Hoy" board, call status, theme and the burger. Without JS the burger is replaced by plain links.
14. **Animations stop**: the "live" dot pulses twice, then stays still (WCAG 2.2.2); respect `prefers-reduced-motion`.
15. **404 uses absolute site paths** (GitHub Pages serves it at any URL).

## Single source of truth

`data/site.json` holds everything that repeats or changes: classes, sessions, phone, WhatsApp, address, geo, call hours, rating, social links, season, legal owner data, photos. `tools/build.py` generates every page, the sitemap, the timetable share image and the class placeholders from it. Never hand-edit generated HTML.
