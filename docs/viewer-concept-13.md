# Concept 13 viewer coordination

The viewer now follows the selected A openings and B roofs, the Concept 11 site revision and the Concept 08 kitchen revision retained by Concept 13. Concept 12, all previous concept folders and the original style study remain unchanged.

## Geometry sources

- `design/concept-13/area-schedule.json`: rooms, areas, heights, stair, acoustic linings, doors, kitchen and dining-chair footprints.
- `design/concept-13/selected-style-geometry.json`: opening rectangles, main hip-roof faces, terrace roof and posts, front canopy, palette and reveals.
- `design/concept-13/rendering-geometry.json`: lot, building placement, court, planning car, sliding gate and reserved sliding space.
- `design/concept-13/roof-coordination.json`: drainage coordination basis and unresolved decisions. The optional viewer overlay transcribes the supplement's candidate collection paths and rear transfer relationships.

Lot coordinates convert by subtracting building x=1.00 m and front depth=5.80 m. Three.js world coordinates are `(building x, height, -building depth)`.

## Visible changes

The main clay hip roof has four planar faces, eaves at +6.60 m and ridge at +7.95 m. Its 9.00 x 10.20 m footprint remains within the lot, with no side projection. The 6.00 x 3.00 m terrace roof slopes from +3.60 to +2.70 m; its outer soffit is +2.50 m. The exposed upper rear setback remains 1.00 m deep. Clay patterns, edge thicknesses and support appearance are illustrative.

The upper bathroom has one 3.10 x 0.55 m opening at +5.15 m, three glazed modules and opaque material representing obscure glass. The two 1.65 x 1.50 m stair windows remain separate at the ground and upper front landings, with 0.20 m ivory reveals. The shortened upper bathroom mirrors stop below the window sill; fixture sizes and sash operation require later coordination.

The 4.80 x 1.85 m car fits the 5.80 m court. The full 3.80 m gate leaf translates 3.80 m alongside the fixed fence, leaving the 3.60 m opening clear. The closed leaf preserves the 0.25 m bumper gap before hardware. Its 1.80 m visual height is an assumption. Vehicle maneuvering, gate hardware and site levels are not simulated.

The refrigerator faces left from the right wall. The sink is on the 3.60 m long counter, with 0.65 m clear between the drawn cooktop and sink. The short return is removed. Dining chairs use the PDF's drawn footprints. Door operation and occupied chair clearances remain subject to appliance/furniture selection; the sink standing space overlaps the nominal refrigerator sweep.

## Controls and limits

Exterior, floor and walk navigation remain. Rear view supplies a direct garden camera. Vehicle gate open toggles the complete leaf between measured positions. Proposed drainage is available only in exterior orbit with roofs visible: blue lines show candidate primary collection and rear transfer relationships; orange lines identify the boundary collection edge and overflow faces. It is a diagram overlay with no sized gutter/pipe mesh. Turning roofs off or entering the house hides the overlay.

A real inset boundary gutter needs a tile-edge setback and may change roof geometry. Its width/depth, falls, primary/overflow outlets, pipe sizes and a permitted site outfall are unresolved. The viewer retains the selected baseline roof until those details are designed. No roof structure, product performance or budget is certified.

Walk collision includes walls, acoustic linings and open interior leaves. Furniture, site enclosure and gates are visual only. Stair ascent/descent and unsupported upper-floor blocking retain the existing tested behavior.

## Verification

The geometry suite checks retained circulation and stair movement plus actual Three.js mesh bounds for roof, terrace, car, gate and kitchen. Browser checks cover desktop/mobile render, room shortcuts, movement, depth cues, gate states, rear view and drainage visibility. Screenshots remain in `viewer/test-results/` for local inspection. The current revision is local; GitHub Pages has not been updated.
