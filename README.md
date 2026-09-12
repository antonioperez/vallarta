# Las Juntas house study

[Open the live walkthrough](https://antonioperez.github.io/vallarta/) · [Source repository](https://github.com/antonioperez/vallarta)

An interactive, browser-based walkthrough of Concept 06: a two-story, three-bedroom house on a 10 × 20 m lot. Built with TypeScript, Vite and Three.js. No viewer installation, account, paid modeling software or backend is needed.

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
- Room shortcuts enter a selected space at 1.65 m eye height, facing useful room features. Walls, acoustic lining reservations and open door leaves have collision; furnishings do not.
- Depth cues (on by default) add architectural edges and soft screen-space corner/contact shading during walking. Turn them off for a lighter rendering path. Distinct wall/ceiling colors, skirting, door frames and locally generated 60 cm tile joints make boundaries and scale easier to read. Materials remain illustrative.
- The twenty stair risers connect both floors. Movement into unsupported upper-floor areas is blocked.
- Roof visibility applies to the exterior orbit view. Floor views automatically remove overhead geometry, and walk mode restores ceilings. Furniture can be hidden.

## Source and accuracy

`design/concept-06/area-schedule.json` supplies room dimensions, areas, floor levels and stair geometry. Walls, openings and furniture positions in `viewer/src/house.ts` and `model.ts` are transcribed from `design/concept-06/draw_house.py`. The model maps building-local plan X to world X and plan Y to negative world Z, in meters.

Ground clear ceiling: 3.00 m. Upper clear ceiling: 2.80 m. Provisional floor-to-floor rise: 3.40 m. The upper opening is 2.25 × 3.59 m. Concept 06 moves the TV to the exterior wall, revises the sofa/chairs, shifts the front entrance, adds stair/service doors, and reserves 0.10 m acoustic linings. The doors are shown held open at the approved swings for navigation. Roof build-up, window and door heights, materials, planting and site enclosures are illustrative. Furniture is simplified. No surveyed north is asserted. This remains a schematic concept, not construction documentation; stair headroom, structure and local compliance are not verified.

The original design sources and PDFs remain in `design/` and are not copied to the published website. They remain visible in the public source repository.

## Verification

```sh
cd viewer
npm test
npm run build
npx playwright install chromium
npm run test:browser
```

Geometry tests check source heights, openings, service access, room viewpoints, full stair ascent/descent and collision boundaries. Browser tests check render startup, crawler meta tags in server-delivered HTML, floor/room controls, wall collision, mobile layout, touch navigation and the depth-cue toggle. Browser screenshots are written under `viewer/test-results/`.

## GitHub Pages

The `Publish house walkthrough` workflow tests and builds the app on pushes to `main`, then publishes only `viewer/dist` with GitHub Actions. The relative Vite asset base supports the `/vallarta/` project path. Choose GitHub Actions as the Pages build source.

## Search indexing

All published HTML entry points include `noindex, nofollow, noimageindex` before JavaScript runs. The production build fails if the index directive is missing; the generated 404 page also has it. No sitemap, search registration or analytics is configured. Fonts are self-hosted.

Crawling is deliberately allowed so compliant search engines can read `noindex`. Do not add `Disallow: /`: it can prevent crawlers from seeing the page's indexing directive. A robots.txt at `/vallarta/robots.txt` is not authoritative for the host; crawler rules are read from the domain-root `/robots.txt`. HTML meta tags are the operative mechanism here.

The site is public. These directives ask compliant engines not to index the HTML; they are not access control, do not control noncompliant bots, and do not prevent GitHub's public source repository from appearing in searches. See Google's [noindex documentation](https://developers.google.com/search/docs/crawling-indexing/block-indexing).
