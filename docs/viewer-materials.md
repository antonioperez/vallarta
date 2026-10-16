# Realistic surface materials

The Concept 14 geometry is retained. Realistic materials are enabled by default and can be disabled independently of depth cues. Source dimensions, collision, gate operation, area units and search-indexing directives are unchanged.

Wood cabinets, doors and tables use scanned grain with normal and roughness maps. Stone floors retain an approximately 60 cm module, now aligned across room boundaries. Clay roofs use color, normal and roughness scans oriented along each roof face. Plaster and fabric use surface/roughness scans with the existing paint and upholstery colors. Bedding has a separate fabric finish so bathroom porcelain and countertops remain smooth. Metal, glass and ceramic gain reflections from a generated neutral lighting environment; those reflections are illustrative and do not mirror the actual room.

UV coordinates are measured in meters on each box face, floor and roof, so enlarging an object does not enlarge its grain. The visual geometry remains schematic; surface maps do not create detailed appliances, rounded furniture or construction assemblies.

The kitchen now includes individual wood base-cabinet fronts, cooktop/prep drawers, paired sink and return doors, recessed toe kicks, and dark metal pulls. Four wall-cabinet doors sit above the prep/sink side, leaving the cooktop area open. All base fronts and pulls fit under the existing L-shaped countertop overhang; wall units are 35 cm deep with their underside at 1.55 m and top at 2.40 m. These are illustrative cabinet modules for the walkthrough, not fabrication drawings; appliance, hood and plumbing coordination remains as recorded in Concept 14.

## Assets and loading

Thirteen self-hosted 1K JPEG maps total 5.57 MiB. Texture objects are shared per finish, with mipmaps and anisotropy capped at four. Software renderers such as SwiftShader use a 240,000-pixel cap for the canvas and depth passes, 512-pixel shadows, and anisotropy capped at one; HTML controls remain sharp. Hardware GPUs retain the existing full-resolution path. There is no live texture-service dependency or subscription. A material set is applied only after all of its files load; failed sets retain their original surfaces and the viewer reports partial loading. Disabling realistic materials restores original maps/colors/roughness and removes environment illumination. The depth-cue toggle separately controls ambient occlusion.

The source assets are [Poly Haven CC0 assets](https://polyhaven.com/license). A one-time API lookup and direct downloads were used for preparation. No API calls run in the published viewer. `viewer/public/textures/sources.json` records original asset pages, download URLs, file sizes and SHA-256 checksums. The original downloaded JPEGs are retained without image processing.

| Finish | Source | Maps used |
|---|---|---|
| Plaster | [White Plaster 02](https://polyhaven.com/a/white_plaster_02) | OpenGL normal, roughness |
| Wood | [Wood Table 001](https://polyhaven.com/a/wood_table_001) | Color, OpenGL normal, roughness |
| Upholstery | [Fabric Pattern 07](https://polyhaven.com/a/fabric_pattern_07) | OpenGL normal, roughness; original solid colors retained |
| Flooring | [Floor Tiles 08](https://polyhaven.com/a/floor_tiles_08) | Color, OpenGL normal, roughness |
| Roof | [Clay Roof Tiles 02](https://polyhaven.com/a/clay_roof_tiles_02) | Color, OpenGL normal, roughness |

Browser checks wait for texture loading, exercise the material switch and simulate missing wood maps to verify the fallback. Desktop/mobile screenshots cover exterior, kitchen, living room and bathrooms. The existing geometry and navigation checks remain in the deployment pipeline.
