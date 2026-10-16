# Build your own house study with an AI assistant

This project grew through a conversation: describe the household and site, inspect a first layout, revise specific decisions, compare appearances, and turn the adopted geometry into a browser walkthrough. The reusable part is how you provide context and check each revision.

The result is a **concept study**: an editable brief, dimensioned drawings, illustrative images and an interactive model. These help communicate decisions to an architect and engineer; they do not establish buildability, structural capacity or construction details.

The prompt examples below are **reconstructed templates**, based on this repository's saved briefs and image prompts. They are not a verbatim conversation or a guarantee that another model will reproduce the same output. Links point to the actual artifacts behind the examples. Start at [the current design index](../design/CURRENT.md) to explore the finished study.

## 1. Give the assistant a useful starting packet

You need an assistant that can work with files and run code to reproduce the drawing and viewer workflow. Image generation or editing is a separate capability. In a text-only chat, you will need to save files and execute the supplied code yourself.

Start with a short brief that separates facts, preferences and unknowns:

| Context | What to provide |
|---|---|
| Site | Lot width/depth, street edge, access and known constraints. Label estimates. Use a generic climate/region in public files. |
| Household | Bedrooms, beds, regular and occasional occupancy, parking and outdoor use. |
| Daily routes | How people reach bathrooms, laundry, kitchen, stairs and patio; privacy or noise concerns. |
| Priorities | What must fit, what is optional, and what can shrink if space runs out. |
| Appearance | A few references, with the feature you like in each: roof, openings, materials or atmosphere. |
| Unknowns | Surveyed orientation, grade, setbacks, structure, drainage and any other information you have not established. |
| Deliverables | Editable sources, dimensioned PDF, area schedule, images and eventually a viewer. |

For an existing property, keep private evidence separately and provide only the relevant measurements to the public project. You do not need an address or map pin to explore a schematic room arrangement.

**Starting prompt:**

```text
Help me develop a conceptual two-story vacation house on a rectangular
10 m × 20 m lot in a warm coastal region. The 10 m edge faces the street.
We need three bedrooms sleeping up to eight, one parking space, shared
bathroom access and a covered rear patio. No pool. I like warm plaster,
timber and clay details.

Treat these as planning inputs, not a surveyed or approved site. Ask about
missing information that would materially change the layout; otherwise
state your assumptions. Do not invent north, setbacks or structural sizes.

First save a brief with fixed requirements, preferences and open questions.
Then propose a dimensioned schematic layout and explain the main tradeoffs.
Use meters as the source units, with decimal feet and square feet alongside.
Separate internal room areas, gross floor areas and covered outdoor areas.
Keep editable drawing sources and a machine-readable area schedule.
```

See [Concept 01's brief](../design/concept-01/brief.md). Its bathroom arrangement and geometry are historical starting decisions, not the current design.

## 2. Put the conversation's decisions into files

Chat history becomes hard to navigate. After accepting a revision, save what changed, why, what stayed fixed and what remains unresolved. Keep earlier concepts and use one small index to select the adopted version.

This repository uses:

- [CURRENT.md](../design/CURRENT.md) to identify the adopted concept and supporting documents.
- A [brief](../design/concept-14/brief.md) for decisions and assumptions.
- [Area and room data](../design/concept-14/area-schedule.json), [site/rendering geometry](../design/concept-14/rendering-geometry.json) and [selected openings/roof geometry](../design/concept-14/selected-style-geometry.json) for measurements.
- [Drawing source](../design/concept-14/draw_house.py), exported PDFs and images for different ways of inspecting the design.
- [Viewer coordination notes](viewer-concept-14.md) for how the adopted design maps to the browser model.

State which source controls each decision. A measured opening should win over a prettier generated image. If two measured records disagree, resolve the conflict before editing. Older briefs can describe their version as “current”; the central index determines what is adopted now.

**Checkpoint or new-session prompt:**

```text
Read design/CURRENT.md, then the adopted brief and geometry files it points
to. Summarize the fixed decisions, unresolved questions and any conflicts.
Use measurements for geometry and generated images only for appearance.

Before changing anything, identify the affected sources and exports.
After an accepted revision, update the brief, related measurements and
current index together. Preserve earlier alternatives. Record what was
actually checked, what was not checked and any known mismatch.
```

Version folders preserve design alternatives; Git records changes within them. Neither replaces a clear adopted-version pointer.

## 3. Ask for a bounded change and its consequences

The most useful follow-ups name the baseline, the problem, the requested change and the constraints to preserve. Include why you want the change so the assistant can catch a solution that technically follows the words but misses the intent.

**Revision prompt:**

```text
Starting from the adopted concept, revise the bathroom/laundry access.
I want people to reach both from inside, without crossing a bedroom or
walking outdoors. Keep the bathroom away from the kitchen wall.

Preserve the lot, bedroom count, sleeping capacity and exterior footprint.
Show the route from the entry hall to each door, including door swings.
Trace any effects on adjacent rooms and furniture. If the constraints
cannot all fit, explain the tradeoff before choosing one to relax.

Save the next concept with updated plans, areas and a short change note.
Show me the changed detail at a readable scale before I accept it.
```

Concrete lessons from the revisions:

| Decision | Why a vague prompt was insufficient | Saved example |
|---|---|---|
| Shared bathrooms and indoor laundry access | A room label does not prove a usable route; trace the hall, passage and doors. | [Concept 02](../design/concept-02/brief.md), [Concept 03](../design/concept-03/brief.md) |
| Open bathroom layout | Removing a separate toilet compartment is different from removing the toilet. “Far end” needed a reference to the entrance. | [Concept 04](../design/concept-04/brief.md) |
| Higher ceilings | A 3.40 m floor rise required a revised stair, a longer bay and changes to adjacent kitchen and bedroom geometry. | [Concept 05](../design/concept-05/brief.md) |
| Sliding vehicle gate | A plausible open image did not demonstrate that the complete leaf could cover the opening and fit its runback. | [Concept 09](../design/concept-09/brief.md) |
| Longer planning car | Increasing the front court consumed depth elsewhere on the fixed lot. | [Concept 11](../design/concept-11/brief.md) |
| L-shaped kitchen and indoor dining | Restoring the return affected the fridge, backing wall and circulation, while the selected exterior remained fixed. | [Concept 14](../design/concept-14/brief.md) |

Ask the assistant to restate ambiguous spatial instructions before changing a drawing. Define left/right from a named viewpoint, and distinguish lot coordinates, building coordinates and image coordinates.

## 4. Give image references distinct jobs

A generated image can quietly change the building to make the composition more attractive. In this project, measured massing and elevation references were used to correct proportions, opening positions, upper-floor setbacks and garden depth.

Do not just attach several images and say “combine these.” Assign authority to each one.

**Measured-model-to-image prompt:**

```text
Create a rear appearance image using these attached references.
Reference 1 controls measured massing, camera direction and site depth.
Reference 2 supplies materials and lighting only.
Reference 3 controls the measured opening locations and widths.

Preserve the floor count, building proportions, upper-floor setback,
canopy extent and every opening from the measured references. Do not copy
different geometry or a deeper garden from the materials reference.
Describe left/right as seen from the garden looking toward the house.
Keep the same camera so I can compare the result against Reference 1.
No extra openings, balcony, pool or story. No text or labels.
```

The [saved Concept 07 prompts](../design/concept-07/image-refinement-prompts.json) show this hierarchy in detail. Their dimensions and facade features belong to that historical concept; do not reuse them as current requirements.

For a bad result, identify the visible error and narrow the next edit. Avoid responding with only “make it more accurate.”

```text
The doorway is the correct total width, but the parked glass occupies
only a quarter of the opening. It should contain two equal-width leaves
overlapping in one half, leaving the other half clear.

Edit only the panel arrangement inside the marked opening. Preserve the
opening boundary, surrounding architecture, kitchen, furniture, materials,
lighting and camera. Return the edited image for comparison.
```

The [saved slider correction](../design/concept-14/final-slider-edit-prompt.txt) used pixel bounds to locate that opening. Those coordinates apply only to its particular source image. A precise prompt still needs inspection: image editing does not guarantee pixel preservation or dimensional accuracy. Check the result against the measured model before accepting it.

## 5. Compare alternatives without losing newer decisions

The [three-style study](../design/style-study-01/brief.md) explored appearances on an older site basis. The eventual hybrid used one option's opening layout and another's clay roofs. Meanwhile, the adopted parking court and car dimensions had changed.

Name both the selected features and the geometry that must survive the combination.

```text
Use the current adopted site and floor plans as the baseline. Combine
Option A's opening layout with Option B's clay hip roof and tiled canopy.
The older comparison images are appearance references only.

Preserve the newer parking court, planning car, rear outdoor depth,
room layout and floor heights. List any roof/opening conflicts rather
than silently resolving them. Save the hybrid as a new concept and keep
the original comparison unchanged.
```

See [Concept 12](../design/concept-12/brief.md) for that selection. A reference's visual appeal does not make all of its earlier decisions authoritative again.

## 6. Build the walkthrough from the adopted measurements

Once the main arrangement is stable, a browser model helps inspect scale, routes and how spaces relate. Start with plain geometry before adding realistic materials.

```text
Build a browser walkthrough from the adopted measured records. Use meters
throughout and document the conversion from lot coordinates to model axes.
Do not infer dimensions from the generated appearance images.

First implement the site, floors, walls, openings and stair. Add exterior
orbit views, floor views and room shortcuts. Then add walking with wall
collision and connected stair movement. Make the controls usable on mobile.

Check heights, room bounds, opening positions, gate travel and stair
ascent/descent against the source data. Inspect screenshots from fixed
front, rear and interior views. Record approximations and unresolved
differences before adding furniture, textures or other polish.
```

Here, [design.ts](../viewer/src/design.ts) reads the adopted JSON and converts coordinates. Other model geometry and collision behavior still require implementation and coordination; changing a JSON value does not automatically reconcile every wall, drawing or image. The [viewer notes](viewer-concept-14.md) describe those mappings and limits.

Follow the [README setup and verification commands](../README.md#run-locally) to run this viewer with Node.js 24. For your own study, replace the brief and geometry deliberately rather than assuming a fork is a general floor-plan generator. The PDF sources are Python scripts using ReportLab; regenerating them also requires their image assets and usable fonts. Some scripts reference macOS fonts, so inspect and adapt those paths on another system.

## 7. Verify each representation and leave a useful handoff

Use different checks for different claims:

- **Numbers:** lot allocation, room bounds, area conventions, unit conversions, floor heights and stair arithmetic.
- **Drawings:** render every PDF page and inspect labels, dimensions, clipping, doors, furniture and cross-page consistency.
- **Images:** compare massing, openings, setbacks and movement states against measured references. Attractive images can still be wrong.
- **Viewer:** run geometry and browser checks; inspect desktop/mobile views and walk the actual routes. A screenshot alone does not establish collision behavior.
- **Professional questions:** keep structure, foundations, stair headroom, drainage, site conditions and local requirements explicitly unresolved until reviewed by the appropriate professionals.

The [preliminary structural review](../design/structural-review-01/review.md) is an example of a separate handoff: it identifies an undefined structural system without pretending that a working viewer validates the building.

**Delivery prompt:**

```text
Review this revision against the adopted brief. Report what changed,
which files and exports were updated, which checks actually passed,
and what remains unresolved. Identify stale references or conflicting
dimensions. Do not mark an image or drawing verified unless inspected.

Prepare a handoff with the current concept, measured sources, selected
appearance references, open decisions and questions for the architect
and engineer. Keep proposed details distinct from confirmed decisions.
```

Before publishing, review filenames as well as contents. Remove exact property locations, map links, personal financial details, local filesystem paths and identifying metadata from PDFs and images. Regenerate exports after sanitizing their sources. Previous commits and externally cached copies need separate attention; editing the latest files does not remove earlier disclosures. See [public sharing notes](../README.md#public-sharing).

Keep the next conversation anchored to the saved brief, a named baseline and a concrete question. That makes revisions inspectable and lets another person continue the study without reconstructing every chat message.
