# Concept 06 viewer update

The viewer now reads the Concept 06 room and acoustic schedules. The TV and living furniture follow the source rectangles directly, the entrance shifts to x=4.10 m, the service doorway is 0.90 m at y=1.55 m, and D0/D1/D2 are shown held open at their specified swings. The door leaves remain visible when furniture is hidden and participate in collision checks.

Acoustic lining reservations are full-height geometry with aligned bedroom-door reveals. They reduce clear bedroom bounds and collision space consistently with the room schedule. The layout still has the adopted floor levels, twenty risers and upper stair opening. No acoustic performance is simulated or asserted.

## Interior legibility

The original strong, warm hemisphere light flattened similarly colored surfaces. Reduced ambient intensity, neutral light, lighter ceilings, distinct wall orientations and lining tones, visible skirting and timber door frames now distinguish adjoining planes. Locally generated 60 cm tile joints supply a scale reference; all finish colors and joints remain illustrative.

Depth cues (enabled by default) show faint architectural edges and screen-space ambient occlusion during walking. The 16-sample pass runs at CSS-pixel resolution with multisampled color rendering. Its projection matrices are synchronized after FOV changes so switching from orbit to walking does not corrupt depth reconstruction. Disabling Depth cues bypasses postprocessing and hides the edges, retaining the basic materials and trim.

Room shortcuts include useful facing directions and a slight downward angle, especially in bathrooms and service spaces. The heading has an opaque backing during walking for contrast against the model.

## Verification

Geometry coverage includes lining thickness/reveals, revised bedroom areas, source door positions, open door collisions, the living aisle, service access, all room spawns and complete stair ascent/descent. Browser coverage includes render startup, room/floor navigation, wall collision, mobile controls, the depth-cue toggle, interior views, and static noindex directives. Rendered screenshots are inspected before publication.

The existing public GitHub Pages workflow and indexing directives remain in place.
