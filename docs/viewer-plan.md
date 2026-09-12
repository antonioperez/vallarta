# Concept 05 walkthrough

Approved scope: reuse this repository; TypeScript, Vite, Three.js; publish on GitHub Pages; request exclusion from search indexing.

## Design
Use concept-05/area-schedule.json for rooms, floor levels and stair dimensions. Transcribe wall/opening and furniture coordinates from concept-05/draw_house.py into named viewer geometry. The model uses meters, +Y up, with plan depth mapped to -Z. Keep the original design files unchanged.

Provide exterior, ground and upper views; orbit/pan/zoom; a first-person mode with wall collision, walkable stairs, keyboard and touch controls; room shortcuts and a floor mini-map. Ceilings/roof and furnishings are toggleable. Show a schematic-design note and distinguish illustrative window/door heights and finishes from the adopted measurements.

Publish only the built viewer. Add static noindex,nofollow meta tags to all HTML entry points, including the 404 page. Allow crawler access so noindex is discoverable. GitHub project-level robots.txt is not authoritative at the host root; meta tags are the operative mechanism. Do not claim to block noncompliant bots or indexing of a public source repository.

## Execution
- [x] Build data and geometry, including genuine openings and the upper stair void.
- [x] Build the responsive viewer, room map and navigation.
- [x] Verify room bounds, opening access, stair elevations, browser controls and production assets.
- [ ] Create the public antonioperez/Mehhhico repository, publish through Pages Actions, and verify the live HTML and assets.

## Files
viewer/src/house.ts: dimensions, wall segments and walk surface logic.
viewer/src/model.ts: Three.js geometry and schematic furnishings.
viewer/src/main.ts and style.css: viewer controls, camera and accessible UI.
viewer/tests/: geometry and browser verification.
.github/workflows/pages.yml: test/build/deploy only viewer/dist.
README.md: commands, source provenance, limitations and indexing behavior.
