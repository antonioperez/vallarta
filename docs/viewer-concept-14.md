# Concept 14 viewer coordination

The viewer follows Concept 14's L-shaped kitchen and six-seat dining, with the selected A openings, B roofs and retained Concept 13 site. Concept 13, all previous concepts and the original style study remain unchanged. Publication remains a separate step.

## Geometry sources

- `design/concept-14/area-schedule.json`: rooms, areas, heights, stair, acoustic linings, doors, kitchen and dining-chair footprints.
- `design/concept-14/selected-style-geometry.json`: opening rectangles, main hip-roof faces, terrace roof and posts, front canopy, palette and reveals.
- `design/concept-14/rendering-geometry.json`: lot, building placement, court, planning car, sliding gate and reserved sliding space.
- `design/concept-14/roof-coordination.json`: drainage coordination basis and unresolved decisions. The optional viewer overlay transcribes the supplement's candidate collection paths and rear transfer relationships.

Lot coordinates convert by subtracting building x=1.00 m and front depth=5.80 m. Three.js world coordinates are `(building x, height, -building depth)`.

## Visible changes

The main clay hip roof has four planar faces, eaves at +6.60 m and ridge at +7.95 m. Its 9.00 x 10.20 m footprint remains within the lot, with no side projection. The 6.00 x 3.00 m terrace roof slopes from +3.60 to +2.70 m; its outer soffit is +2.50 m. The exposed upper rear setback remains 1.00 m deep. Clay patterns, edge thicknesses and support appearance are illustrative.

The upper bathroom has one 3.10 x 0.55 m opening at +5.15 m, three glazed modules and opaque material representing obscure glass. The two 1.65 x 1.50 m stair windows remain separate at the ground and upper front landings, with 0.20 m ivory reveals. The shortened upper bathroom mirrors stop below the window sill; fixture sizes and sash operation require later coordination.

The 4.80 x 1.85 m car fits the 5.80 m court. The full 3.80 m gate leaf translates 3.80 m alongside the fixed fence, leaving the 3.60 m opening clear. The closed leaf preserves the 0.25 m bumper gap before hardware. Its 1.80 m visual height is an assumption. Vehicle maneuvering, gate hardware and site levels are not simulated.

The 3.60 m long counter retains its cooktop/sink and 0.65 m preparation gap. A 0.65 × 1.05 m right-wall return restores the L. The fridge body starts at building-local `(8.03, 6.85)` and ends at depth 7.65 m, facing left. The new 1.10 × 0.15 m backing segment at `(5.20, 4.80)` joins the stair wall and reaches the 3.00 m ground ceiling.

A 0.90 × 1.80 m table runs front-to-back with six chairs from the shared PDF records. Their outward vectors orient the backs and the 0.30 m movement test. The terrace retains eight seats. G4/G5 remain reference allocations, with fridge placement checked against their combined open space. The kitchen shortcut looks toward the restored L and moved appliance.

The rear aperture remains 3.20 × 2.50 m. Glazing overlaps in x=6.50-8.10 m, leaving the left half x=4.90-6.50 clear. The same parked-panel rectangle supplies rendering and collision. A continuous 1.00 m route beside the living room turns left of the rear dining seat and passes through this opening. The 0.90 m behind the table is reserved for seating. The rear chair test ends only 0.05 m from the wall; furniture selection and occupied-body clearances remain unverified.

## Controls and limits

Exterior, floor and walk navigation remain. Rear view supplies a direct garden camera. Vehicle gate open toggles the complete leaf between measured positions. Proposed drainage is available only in exterior orbit with roofs visible: blue lines show candidate primary collection and rear transfer relationships; orange lines identify the boundary collection edge and overflow faces. It is a diagram overlay with no sized gutter/pipe mesh. Turning roofs off or entering the house hides the overlay.

A real inset boundary gutter needs a tile-edge setback and may change roof geometry. Its width/depth, falls, primary/overflow outlets, pipe sizes and a permitted site outfall are unresolved. The viewer retains the selected baseline roof until those details are designed. No roof structure, product performance or budget is certified.

Walk collision includes walls, acoustic linings, open interior leaves and the rear slider panels parked right. Furniture, site enclosure and gates are visual only. Stair ascent/descent and unsupported upper-floor blocking retain the existing tested behavior.

## Verification

The geometry suite checks retained circulation and stair movement plus actual Three.js bounds for roof, terrace, car, gate, kitchen, new full-height wall, return, six-seat table/chairs and parked rear panels. Tests sample each chair through its complete 0.30 m outward movement and the nominal fridge leaf through 0-90 degrees. Browser checks cover desktop/mobile render, room shortcuts, movement, depth cues, gate states, rear view and drainage visibility. Screenshots remain in `viewer/test-results/` for local inspection. The current revision is local; GitHub Pages has not been updated.
