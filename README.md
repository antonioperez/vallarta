# Las Juntas house study

[Open the live walkthrough](https://antonioperez.github.io/vallarta/) · [Source repository](https://github.com/antonioperez/vallarta)

An interactive, browser-based walkthrough of Concept 14: a two-story, three-bedroom house on a 10 × 20 m lot. Built with TypeScript, Vite and Three.js. No viewer installation, account, paid modeling software or backend is needed.

## Run locally

Requires Node.js 24 and npm.

```sh
cd viewer
npm ci
npm run dev
```

Open the local URL printed by Vite. `npm run build` produces `viewer/dist`; `npm run preview` serves that production build.

## Explore

- Exterior, ground-floor and upper-floor views support orbit, zoom and pan.
- Walk inside with WASD or arrow keys; drag to look. On-screen arrows also work with touch. Escape returns to orbit.
- Room shortcuts enter a selected space at 1.65 m eye height, facing useful room features. Walls, acoustic lining reservations, open door leaves and parked rear glazing have collision; furnishings do not.
- Depth cues (on by default) add architectural edges and soft screen-space corner/contact shading during walking. Turn them off for a lighter rendering path. Distinct wall/ceiling colors, skirting, door frames and locally generated 60 cm tile joints make boundaries and scale easier to read. Materials remain illustrative.
- The twenty stair risers connect both floors. Movement into unsupported upper-floor areas is blocked.
- The selected exterior combines A’s window layout with B’s clay hip roof and tiled terrace canopy. Use Rear view for the garden elevation. The complete vehicle gate can be shown open or closed.
- Proposed drainage adds diagram lines for collection and rear transfers; it does not show engineered gutter or pipe sizes. Turn it on from the exterior with the roof visible.
- Roof visibility applies to the exterior orbit view. Floor views automatically remove overhead geometry, and walk mode restores ceilings. Furniture can be hidden.

## Source and accuracy

`design/concept-14/area-schedule.json` supplies rooms, areas, floor levels, stair geometry, acoustic reservations and the revised kitchen. `selected-style-geometry.json` supplies the selected openings and roof geometry; `rendering-geometry.json` supplies the current site, car and sliding gate. `viewer/src/design.ts` converts the lot-coordinate geometry to building-local coordinates. The model maps building-local X to world X, plan depth to negative world Z, and height to world Y, in meters.

Ground clear ceiling: 3.00 m; upper: 2.80 m; floor-to-floor: 3.40 m. Main roof eave/ridge: 6.60/7.95 m. The front court is 5.80 m deep for the 4.80 m planning car. The 3.80 m sliding leaf clears the 3.60 m vehicle opening and stays in its reserved runback. The L-shaped kitchen retains the 3.60 m counter and sink, restores the 1.05 m right-wall return, moves the fridge 1.05 m rearward and adds full-height backing. The 0.90 × 1.80 m indoor table seats six; the terrace table seats eight. A 1.00 m living-side route reaches the left half of the rear slider, with glazing parked right. G4/G5 remain reference subzones of one open space. Two separate stair windows and a high, three-module obscure bathroom opening follow the selected A layout.

The main PDF contains 13 pages, including proposed drainage coordination. The model retains the baseline roof: sizing the inset boundary gutter may change its tiled edge and hip/ridge. Colored overlay lines are diagram centerlines only; overflow elevations, pipe sizes and the site outfall remain unresolved. Roof build-up, tile pattern, the 1.80 m gate height, car shape and furniture remain illustrative. Bathroom mirrors stop below the high window; their final specification remains open. The interior doors remain held open at the approved swings. Movement collides with walls, interior door leaves and parked rear glazing, not furniture or site gates. No surveyed north is asserted. Structure, stair headroom, local compliance and the budget are unverified.

See [the current design index](design/CURRENT.md) and [viewer coordination notes](docs/viewer-concept-14.md). Concept 14 was published to the live walkthrough on 13 September 2026.

The original design sources and PDFs remain in `design/` and are not copied to the published website. They remain visible in the public source repository.

## Verification

```sh
cd viewer
npm test
npm run build
npx playwright install chromium
npm run test:browser
```

Geometry tests check source heights, openings, service access, room viewpoints, full stair ascent/descent and collision boundaries, plus actual roof/car/kitchen mesh bounds and the complete gate leaf in both positions. Browser tests check render startup, crawler meta tags in server-delivered HTML, floor/room controls, wall collision, mobile layout, touch navigation, the depth-cue toggle, selected exterior controls and proposed drainage visibility. Browser screenshots are written under `viewer/test-results/`.

## GitHub Pages

The `Publish house walkthrough` workflow tests and builds the app on pushes to `main`, then publishes only `viewer/dist` with GitHub Actions. The relative Vite asset base supports the `/vallarta/` project path. Choose GitHub Actions as the Pages build source.

## Search indexing

All published HTML entry points include `noindex, nofollow, noimageindex` before JavaScript runs. The production build fails if the index directive is missing; the generated 404 page also has it. No sitemap, search registration or analytics is configured. Fonts are self-hosted.

Crawling is deliberately allowed so compliant search engines can read `noindex`. Do not add `Disallow: /`: it can prevent crawlers from seeing the page's indexing directive. A robots.txt at `/vallarta/robots.txt` is not authoritative for the host; crawler rules are read from the domain-root `/robots.txt`. HTML meta tags are the operative mechanism here.

The site is public. These directives ask compliant engines not to index the HTML; they are not access control, do not control noncompliant bots, and do not prevent GitHub's public source repository from appearing in searches. See Google's [noindex documentation](https://developers.google.com/search/docs/crawling-indexing/block-indexing).
