import * as THREE from "three";
import {
  heights,
  livingFurniture,
  openDoorLeaves,
  levels,
  rooms,
  stair,
  wallSolids,
  walls,
  type Floor,
  type View,
} from "./house";
import { addFloorFinish, addEdges } from "./surfaces";
import {
  style,
  geometry,
  site as siteGeometry,
  gate,
  lotRect,
  lotPoint,
  kitchen,
  rearSliderPanelRect,
  mainRoofFaces,
  terraceRoofFace,
  proposedCollectionPaths,
  proposedFlowArrows,
  type Point,
} from "./design";
import { addClayRoof, worldPoint } from "./roof";

const palette = {
  plaster: "#eee5d6",
  stone: "#a9a596",
  tile: "#bca487",
  wood: "#9a6545",
  cream: "#f7f0e4",
  sage: "#819080",
  rust: "#a4573e",
  metal: "#49413a",
  glass: "#b5cfda",
  ceiling: "#f4f3ed",
  sideWall: "#ccd4cd",
  lining: "#bacbc1",
  trim: "#797b6c",
};
const cube = new THREE.BoxGeometry(1, 1, 1);
const materials = new Map<string, THREE.MeshStandardMaterial>();
function material(color: string, glass = false) {
  const key = color + glass;
  if (!materials.has(key))
    materials.set(
      key,
      new THREE.MeshStandardMaterial({
        color,
        roughness: glass ? 0.15 : 0.86,
        metalness: 0,
        emissive: color === palette.ceiling ? palette.ceiling : "#000000",
        emissiveIntensity: color === palette.ceiling ? 0.18 : 0,
        transparent: glass,
        opacity: glass ? 0.27 : 1,
        depthWrite: !glass,
      }),
    );
  return materials.get(key)!;
}
// Boxes accept the original plan coordinates; depth increases toward the rear.
function box(
  parent: THREE.Group,
  x: number,
  d: number,
  w: number,
  depth: number,
  bottom: number,
  height: number,
  color = palette.plaster,
  glass = false,
): THREE.Mesh {
  const mesh = new THREE.Mesh(cube, material(color, glass));
  mesh.position.set(x + w / 2, bottom + height / 2, -d - depth / 2);
  mesh.scale.set(w, height, depth);
  mesh.castShadow = !glass;
  mesh.receiveShadow = true;
  parent.add(mesh);
  return mesh;
}
function cylinder(
  parent: THREE.Group,
  x: number,
  d: number,
  y: number,
  r: number,
  height: number,
  color: string,
) {
  const mesh = new THREE.Mesh(
    new THREE.CylinderGeometry(r, r * 0.85, height, 12),
    material(color),
  );
  mesh.position.set(x, y + height / 2, -d);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  parent.add(mesh);
}
function bed(
  group: THREE.Group,
  x: number,
  d: number,
  w: number,
  depth: number,
  base: number,
  right = false,
) {
  box(group, x, d, w, depth, base + 0.1, 0.24, palette.wood);
  box(
    group,
    x + 0.025,
    d + 0.025,
    w - 0.05,
    depth - 0.05,
    base + 0.34,
    0.25,
    palette.cream,
  );
  box(
    group,
    x + 0.035,
    d + 0.08,
    w - 0.07,
    depth * 0.55,
    base + 0.59,
    0.045,
    palette.sage,
  );
  if (right) {
    box(group, x + w - 0.1, d, 0.09, depth, base + 0.15, 0.9, palette.wood);
    for (const p of [d + 0.2, d + depth / 2 + 0.1])
      box(group, x + w - 0.55, p, 0.4, 0.6, base + 0.59, 0.12, palette.cream);
  } else {
    box(group, x, d + depth - 0.1, w, 0.09, base + 0.15, 0.9, palette.wood);
    for (const p of [x + 0.12, x + w / 2 + 0.05])
      box(
        group,
        p,
        d + depth - 0.52,
        w / 2 - 0.18,
        0.38,
        base + 0.59,
        0.12,
        palette.cream,
      );
  }
}
function table(group: THREE.Group, x: number, d: number, base: number) {
  box(group, x, d, 2.2, 0.95, base + 0.73, 0.08, palette.wood);
  for (const dx of [0.12, 1.98])
    for (const dz of [0.12, 0.73])
      box(group, x + dx, d + dz, 0.08, 0.08, base, 0.73, palette.wood);
  for (const dx of [0.12, 0.82, 1.52])
    for (const dz of [-0.47, 1.04]) {
      box(group, x + dx, d + dz, 0.46, 0.4, base + 0.41, 0.09, palette.sage);
      box(
        group,
        x + dx,
        d + dz + (dz < 0 ? 0 : 0.34),
        0.46,
        0.06,
        base + 0.48,
        0.34,
        palette.wood,
      );
    }
  for (const dx of [-0.48, 2.25])
    box(group, x + dx, d + 0.23, 0.4, 0.46, base + 0.4, 0.12, palette.sage);
  cylinder(group, x + 1.1, d + 0.47, base + 0.81, 0.13, 0.23, palette.rust);
}
function vanity(
  group: THREE.Group,
  x: number,
  d: number,
  w: number,
  base: number,
  double = false,
  mirrorHeight = 0.8,
) {
  box(group, x, d, w, 0.55, base + 0.15, 0.65, palette.wood);
  box(group, x, d, w, 0.55, base + 0.8, 0.06, palette.cream);
  const centers = double ? [x + 0.42, x + w - 0.42] : [x + w / 2];
  for (const cx of centers) {
    box(
      group,
      cx - 0.23,
      d + 0.1,
      0.46,
      0.33,
      base + 0.86,
      0.04,
      palette.glass,
    );
    box(
      group,
      cx - 0.015,
      d + 0.06,
      0.03,
      0.05,
      base + 0.86,
      0.2,
      palette.metal,
    );
    box(
      group,
      cx - 0.27,
      d + 0.01,
      0.54,
      0.025,
      base + 1.08,
      mirrorHeight,
      palette.glass,
    );
  }
}
function toilet(
  group: THREE.Group,
  x: number,
  d: number,
  base: number,
  reverse = false,
) {
  box(group, x, d + (reverse ? 0.55 : 0), 0.6, 0.2, base, 0.75, palette.cream);
  cylinder(
    group,
    x + 0.3,
    d + (reverse ? 0.28 : 0.48),
    base + 0.1,
    0.22,
    0.32,
    palette.cream,
  );
}

export function createHouse(scene: THREE.Scene) {
  const depthEdges: THREE.LineSegments[] = [];
  let depthCuesEnabled = true;
  const site = new THREE.Group(),
    ground = new THREE.Group(),
    upper = new THREE.Group(),
    roof = new THREE.Group();
  const furniture: Record<Floor, THREE.Group> = {
    ground: new THREE.Group(),
    upper: new THREE.Group(),
  };
  ground.add(furniture.ground);
  upper.add(furniture.upper);
  site.name = "Site";
  ground.name = "Ground floor";
  upper.name = "Upper floor";
  roof.name = "Selected clay roofs and canopies";
  scene.add(site, ground, upper, roof);
  const front = siteGeometry.front_depth,
    rear = siteGeometry.lot_depth - front;
  box(site, -1, -front, 10, 20, -0.22, 0.2, "#c6beac");
  box(site, -1, 10.5, 10, rear - 10.5, -0.02, 0.035, "#a1a785");
  box(site, 2, 10.5, 6, 3, 0.015, 0.07, palette.tile);
  box(site, -1, -front - 2, 10, 2, -0.25, 0.04, "#a3a39a");
  // Flush vehicle crossing; no curb or planting across its exit corridor.
  for (const x of [-1, 8.9])
    box(site, x, -front, 0.1, 20, 0, 0.8, palette.stone);
  box(site, -1, rear - 0.1, 10, 0.1, 0, 1.2, palette.stone);
  box(site, 7.65, -front + 0.45, 1.0, 4.3, 0.01, 0.025, "#e9e4d8");
  box(site, 4.3, -1.1, 4.35, 0.9, 0.01, 0.025, "#e9e4d8");
  for (const r of style.rear_canopy_columns_lot_xywh)
    box(
      site,
      ...lotRect(r),
      0.08,
      style.rear_canopy.soffit - 0.08,
      palette.wood,
    );
  table(site, 4, 11.5, 0.08);

  const gateLeaf = new THREE.Group();
  gateLeaf.name = "Complete sliding gate leaf";
  site.add(gateLeaf);
  const gateHeight = 1.8; // Appearance only; no gate structure or height selected.
  const panel = (parent: THREE.Group, r: readonly number[]) => {
    const [x, d, w, depth] = lotRect(r);
    box(parent, x, d, w, depth, 0.08, gateHeight - 0.08, palette.metal);
    for (let y = 0.3; y < gateHeight; y += 0.18)
      box(
        parent,
        x + 0.04,
        d + depth - 0.008,
        w - 0.08,
        0.008,
        y,
        0.018,
        "#706156",
      );
  };
  panel(gateLeaf, gate.closed_leaf);
  panel(site, gate.fixed_fence);
  for (const r of gate.posts)
    box(site, ...lotRect(r), 0, gateHeight + 0.08, palette.plaster);
  box(site, -1, -front, 0.6, 0.12, 0, gateHeight, palette.plaster);
  box(site, 8.85, -front, 0.15, 0.12, 0, gateHeight, palette.plaster);
  // Separate pedestrian leaf held inward, out of the retained sliding reserve.
  box(site, 8.6, -front + 0.22, 0.045, 1.05, 0, gateHeight, palette.metal);
  gateLeaf.position.x = gate.travel;

  // Body and wheels fit the 1.85 x 4.80 m planning envelope.
  const car = new THREE.Group();
  car.name = "4.80 m planning car";
  site.add(car);
  const [cx, cd, cw, cl] = lotRect(geometry.parking_m.car);
  box(car, cx, cd, cw, cl, 0.28, 0.52, "#7b8c87");
  box(car, cx + 0.14, cd + 1.0, cw - 0.28, 2.35, 0.8, 0.65, "#a5b9b6");
  for (const d of [cd + 1.02, cd + 3.26])
    box(car, cx + 0.19, d, cw - 0.38, 0.055, 0.98, 0.38, palette.glass);
  for (const x of [cx + 0.09, cx + cw - 0.09])
    for (const d of [cd + 0.82, cd + cl - 0.85]) {
      const wheel = new THREE.Mesh(
        new THREE.CylinderGeometry(0.29, 0.29, 0.18, 20),
        material("#303635"),
      );
      wheel.rotation.z = Math.PI / 2;
      wheel.position.set(x, 0.3, -d);
      wheel.castShadow = true;
      car.add(wheel);
    }

  const drainage = new THREE.Group();
  drainage.name = "Proposed drainage diagram";
  roof.add(drainage);
  drainage.visible = false;
  const flowMaterial = new THREE.LineBasicMaterial({
    color: "#168eaf",
    depthTest: false,
  });
  const dashedMaterial = new THREE.LineDashedMaterial({
    color: "#168eaf",
    dashSize: 0.16,
    gapSize: 0.1,
    depthTest: false,
  });
  const diagramLine = (points: Point[], dashed = false, color?: string) => {
    const m = color
      ? new THREE.LineBasicMaterial({ color, depthTest: false })
      : dashed
        ? dashedMaterial
        : flowMaterial;
    const line = new THREE.Line(
      new THREE.BufferGeometry().setFromPoints(points.map(worldPoint)),
      m,
    );
    line.computeLineDistances();
    line.renderOrder = 10;
    drainage.add(line);
  };
  for (const path of proposedCollectionPaths) diagramLine(path);
  diagramLine(
    [lotPoint([9.85, 5.55], 6.67), lotPoint([9.85, 15.55], 6.67)],
    false,
    "#db792e",
  );
  for (const points of proposedFlowArrows) {
    const start = worldPoint(points[0]),
      end = worldPoint(points[1]),
      delta = end.clone().sub(start);
    const arrow = new THREE.ArrowHelper(
      delta.clone().normalize(),
      start,
      delta.length(),
      "#168eaf",
      0.3,
      0.17,
    );
    arrow.traverse((o) => {
      if (o instanceof THREE.Line || o instanceof THREE.Mesh) {
        (o.material as THREE.Material).depthTest = false;
        o.renderOrder = 10;
      }
    });
    drainage.add(arrow);
  }
  // Rear transfer shown as a relationship only; no constructed pipe diameter.
  for (const x of [1.1, 9.85])
    diagramLine(
      [
        lotPoint([x, 15.55], 6.67),
        lotPoint([x, 15.55], 3.6),
        lotPoint([x, 16.3], 3.6),
        lotPoint([x, 16.3], 0.3),
      ],
      true,
    );
  for (const y of [5.45, 15.65]) {
    const endY = y < 10 ? 4.8 : 16.15;
    diagramLine(
      [lotPoint([9.5, y], 6.72), lotPoint([9.5, endY], 6.72)],
      false,
      "#db792e",
    );
  }

  box(ground, 0, 0, 9, 10.5, -0.1, 0.1, palette.tile);
  // The upper slab is split around the measured stair opening.
  const slabBottom = heights.ground_clear,
    slabHeight = heights.floor_to_floor - slabBottom;
  for (const r of [
    [0, 0, 6.4, 9.5],
    [8.65, 0, 0.35, 9.5],
    [6.4, 0, 2.25, 1.2],
    [6.4, 4.79, 2.25, 4.71],
  ]) {
    const slab = box(
      upper,
      r[0],
      r[1],
      r[2],
      r[3],
      slabBottom,
      slabHeight,
      palette.tile,
    );
    slab.material = [
      material(palette.stone),
      material(palette.stone),
      material(palette.tile),
      material(palette.ceiling),
      material(palette.stone),
      material(palette.stone),
    ];
  }
  box(roof, 0, 0, 9, 9.5, heights.upper_ceiling_level, 0.12, palette.ceiling);
  // Fill the selected eave band above the clear upper ceiling; roof build-up is schematic.
  for (const [x, d, w, depth] of [
    [0, 0, 9, 0.2],
    [0, 9.3, 9, 0.2],
    [0, 0.2, 0.2, 9.1],
    [8.8, 0.2, 0.2, 9.1],
  ])
    box(
      roof,
      x,
      d,
      w,
      depth,
      heights.upper_ceiling_level,
      style.roof.main_top - heights.upper_ceiling_level,
      palette.plaster,
    );
  box(
    roof,
    0,
    9.5,
    9,
    1,
    heights.ground_clear,
    heights.floor_to_floor - heights.ground_clear,
    palette.ceiling,
  );
  addClayRoof(roof, mainRoofFaces, 0.12, "Main hip roof");
  addClayRoof(
    roof,
    [terraceRoofFace],
    style.rear_canopy.low_top - style.rear_canopy.soffit,
    "Terrace clay roof",
  );
  box(
    roof,
    ...lotRect(style.front_canopy.footprint_lot),
    style.front_canopy.soffit,
    style.front_canopy.top - style.front_canopy.soffit,
    palette.wood,
  );
  for (const floor of ["ground", "upper"] as const) {
    const group = floor === "ground" ? ground : upper,
      base = levels[floor];
    for (const s of wallSolids(floor)) {
      const color = s.lining
        ? palette.lining
        : s.w > s.d
          ? palette.plaster
          : palette.sideWall;
      const wall = box(
        group,
        s.x,
        s.z,
        s.w,
        s.d,
        s.bottom,
        s.top - s.bottom,
        color,
      );
      if (s.name) wall.name = s.name;
      depthEdges.push(addEdges(wall));
      if (s.bottom === base) {
        // Skirting stops at each actual door opening and outlines the floor junction.
        box(
          group,
          s.x - 0.012,
          s.z - 0.012,
          s.w + 0.024,
          s.d + 0.024,
          base,
          0.095,
          palette.trim,
        );
      }
    }
    for (const wall of walls[floor]) {
      const [x, d, w, depth] = wall.rect,
        horizontal = w > depth;
      for (const o of wall.openings ?? []) {
        if (o.kind === "door") {
          // Jambs sit outside the nominal opening. Linings share the same reveal.
          const frame = palette.wood;
          if (horizontal) {
            for (const edge of [o.start - 0.045, o.start + o.width])
              box(
                group,
                edge,
                d - 0.018,
                0.045,
                depth + 0.036,
                base,
                o.height,
                frame,
              );
            box(
              group,
              o.start - 0.045,
              d - 0.018,
              o.width + 0.09,
              depth + 0.036,
              base + o.height,
              0.055,
              frame,
            );
          } else {
            for (const edge of [o.start - 0.045, o.start + o.width])
              box(
                group,
                x - 0.018,
                edge,
                w + 0.036,
                0.045,
                base,
                o.height,
                frame,
              );
            box(
              group,
              x - 0.018,
              o.start - 0.045,
              w + 0.036,
              o.width + 0.09,
              base + o.height,
              0.055,
              frame,
            );
          }
          if (horizontal && d > 10) {
            const [px, pd, pw] = rearSliderPanelRect;
            const panels = new THREE.Group();
            panels.name = "Rear slider parked panels";
            group.add(panels);
            for (const offset of [0, 0.045]) {
              box(
                panels,
                px,
                pd + offset,
                pw,
                0.035,
                base + 0.03,
                o.height - 0.06,
                palette.glass,
                true,
              );
              for (const edge of [px, px + pw - 0.035])
                box(
                  panels,
                  edge,
                  pd + offset,
                  0.035,
                  0.035,
                  base,
                  o.height,
                  palette.metal,
                );
              for (const height of [base, base + o.height - 0.035])
                box(
                  panels,
                  px,
                  pd + offset,
                  pw,
                  0.035,
                  height,
                  0.035,
                  palette.metal,
                );
            }
          }
          continue;
        }
        const wx = horizontal ? o.start : x + w / 2 - 0.015;
        const wz = horizontal ? d + depth / 2 - 0.015 : o.start;
        box(
          group,
          wx,
          wz,
          horizontal ? o.width : 0.03,
          horizontal ? 0.03 : o.width,
          base + o.sill,
          o.height,
          o.privacy ? "#d9dfd6" : palette.glass,
          !o.privacy,
        );
        if (horizontal) {
          if (o.reveal) {
            for (const px of [o.start - 0.1, o.start + o.width])
              box(
                group,
                px,
                -o.reveal,
                0.1,
                o.reveal + 0.04,
                base + o.sill - 0.1,
                o.height + 0.2,
                palette.plaster,
              );
            for (const py of [base + o.sill - 0.1, base + o.sill + o.height])
              box(
                group,
                o.start,
                -o.reveal,
                o.width,
                o.reveal + 0.04,
                py,
                0.1,
                palette.plaster,
              );
          }
          for (const dx of Array.from(
            { length: (o.modules ?? 2) + 1 },
            (_, i) =>
              Math.min(o.width - 0.025, (i * o.width) / (o.modules ?? 2)),
          ))
            box(
              group,
              o.start + dx,
              d + 0.04,
              0.025,
              0.05,
              base + o.sill,
              o.height,
              palette.metal,
            );
          for (const dy of [0, o.height - 0.025])
            box(
              group,
              o.start,
              d + 0.04,
              o.width,
              0.05,
              base + o.sill + dy,
              0.025,
              palette.metal,
            );
        } else {
          for (const dz of [0, o.width / 2, o.width - 0.025])
            box(
              group,
              x + 0.04,
              o.start + dz,
              0.05,
              0.025,
              base + o.sill,
              o.height,
              palette.metal,
            );
        }
      }
    }
    for (const room of rooms.filter((r) => r.floor === floor)) {
      const [x, d, w, depth] = room.rect;
      if (room.id === "G7" || room.id === "U7") continue;
      addFloorFinish(
        group,
        x,
        d,
        w,
        depth,
        base + 0.012,
        /bathroom/.test(room.name)
          ? "#8daaa7"
          : /bedroom/.test(room.name)
            ? "#c2a483"
            : palette.tile,
      );
    }
  }
  // Two flights of nine treads and a turning landing = twenty risers total.
  for (let i = 0; i < 9; i++) {
    box(
      ground,
      6.4,
      1.2 + i * 0.28,
      1.05,
      0.28,
      0,
      (i + 1) * 0.17,
      palette.stone,
    );
    const top = 3.4 - (i + 1) * 0.17;
    box(
      ground,
      7.6,
      1.2 + i * 0.28,
      1.05,
      0.28,
      top - 0.13,
      0.13,
      palette.stone,
    );
  }
  box(
    ground,
    6.4,
    stair.flight_back_y,
    2.25,
    stair.turn_landing,
    1.55,
    0.15,
    palette.stone,
  );
  // Thin illustrative handrails; structure/headroom still require a section study.
  for (let i = 0; i < 10; i++) {
    box(
      ground,
      7.47,
      1.2 + i * 0.28,
      0.035,
      0.035,
      Math.min(i + 1, 10) * 0.17,
      0.9,
      palette.metal,
    );
    box(
      ground,
      7.55,
      1.2 + i * 0.28,
      0.035,
      0.035,
      3.4 - Math.min(i + 1, 10) * 0.17,
      0.9,
      palette.metal,
    );
  }
  const g = furniture.ground,
    u = furniture.upper,
    b = levels.upper;
  bed(g, 1.4, 4.42, 1.52, 2.03, 0);
  box(g, 0.2, 2.95, 0.6, 1.25, 0, 2.25, palette.wood);
  box(g, 5.7, 2.6, 0.45, 1.2, 0, 0.85, palette.wood);
  const k = kitchen.rectangles_m;
  const kitchenBox = (
    r: number[],
    bottom: number,
    height: number,
    color: string,
  ) => box(g, r[0], r[1], r[2], r[3], bottom, height, color);
  kitchenBox(k.counter, 0, 0.9, palette.wood).name = "3.60 m kitchen counter";
  kitchenBox(k.counter, 0.9, 0.045, palette.cream);
  kitchenBox(k.return, 0, 0.9, palette.wood).name = "Kitchen right-wall return";
  kitchenBox(k.return, 0.9, 0.045, palette.cream);
  kitchenBox(k.cooktop, 0.95, 0.01, palette.metal).name = "Cooktop";
  for (const x of [k.cooktop[0] + 0.18, k.cooktop[0] + 0.56])
    for (const d of [k.cooktop[1] + 0.11, k.cooktop[1] + 0.32])
      cylinder(g, x, d, 0.96, 0.07, 0.006, "#8b9390");
  kitchenBox(k.sink, 0.95, 0.015, palette.glass).name = "Sink";
  box(
    g,
    k.sink[0] + 0.3,
    k.sink[1] - 0.055,
    0.04,
    0.045,
    0.95,
    0.25,
    palette.metal,
  );
  kitchenBox(k.fridge_body, 0, 1.9, "#afbab4").name = "Right-wall refrigerator";
  // Door face is on the kitchen/left side. Handle opposite the dining-end hinge.
  box(
    g,
    k.fridge_body[0] - 0.018,
    k.fridge_body[1],
    0.018,
    k.fridge_body[3],
    0.05,
    1.82,
    "#d0d4cf",
  );
  box(
    g,
    k.fridge_body[0] - 0.045,
    k.fridge_body[1] + 0.06,
    0.027,
    0.025,
    0.95,
    0.5,
    palette.metal,
  );
  // Six chairs and their orientation come from the shared PDF movement study.
  const [dx, dd, dw, dl] = kitchen.dining_table_m;
  box(g, dx, dd, dw, dl, 0.73, 0.08, palette.wood).name =
    "Six-seat indoor table";
  for (const x of [dx + 0.12, dx + dw - 0.2])
    for (const d of [dd + 0.12, dd + dl - 0.2])
      box(g, x, d, 0.08, 0.08, 0, 0.73, palette.wood);
  kitchen.dining_chairs_drawn_m.forEach(([x, d, w, depth], i) => {
    const chair = new THREE.Group();
    chair.name = `Indoor dining chair ${i + 1}`;
    g.add(chair);
    box(chair, x, d, w, depth, 0.41, 0.09, palette.sage);
    const [vx, vd] = kitchen.chair_outward_vectors[i];
    box(
      chair,
      x + (vx > 0 ? w - 0.06 : 0),
      d + (vd > 0 ? depth - 0.06 : 0),
      vx ? 0.06 : w,
      vd ? 0.06 : depth,
      0.5,
      0.32,
      palette.wood,
    );
    for (const xx of [x + 0.035, x + w - 0.075])
      for (const dd of [d + 0.035, d + depth - 0.075])
        box(chair, xx, dd, 0.04, 0.04, 0, 0.41, palette.wood);
  });
  // Retained acoustic layout: TV on the exterior wall; the three-seat sofa faces it.
  const lf = livingFurniture;
  const place = (r: number[], bottom: number, height: number, color: string) =>
    box(g, r[0], r[1], r[2], r[3], bottom, height, color);
  place(lf.media_console, 0.06, 0.52, palette.wood);
  const tv = place(lf.tv, 0.9, 0.76, palette.metal);
  depthEdges.push(addEdges(tv));
  place(lf.sofa, 0.12, 0.34, palette.sage);
  const [sx, sz, sw, sd] = lf.sofa;
  box(g, sx + sw - 0.15, sz, 0.15, sd, 0.46, 0.45, palette.sage);
  for (let n = 0; n < 3; n++)
    box(
      g,
      sx + 0.04,
      sz + 0.1 + n * 0.8,
      sw - 0.22,
      0.76,
      0.46,
      0.1,
      palette.cream,
    );
  for (const z of [sz, sz + sd - 0.1])
    box(g, sx, z, sw, 0.1, 0.46, 0.24, palette.sage);
  place(lf.coffee_table, 0.18, 0.22, palette.wood);
  for (const r of [lf.chair, lf.rear_chair]) {
    place(r, 0.12, 0.35, palette.rust);
    box(g, r[0], r[1], 0.13, r[3], 0.47, 0.37, palette.rust);
  }
  // Solid-core doors are held open at the approved swings for the walkthrough.
  for (const [index, r] of openDoorLeaves.entries()) {
    const leaf = box(
      ground,
      r[0],
      r[1],
      r[2],
      r[3],
      0.02,
      (index === 0 ? style.front_openings.entry[3] : 2.2) - 0.05,
      palette.wood,
    );
    depthEdges.push(addEdges(leaf));
    box(
      ground,
      r[0] + r[2] * 0.8,
      r[1] + r[3] * 0.8,
      0.06,
      0.06,
      0.98,
      0.035,
      palette.metal,
    );
  }
  vanity(g, 1.3, 0.2, 0.9, 0);
  toilet(g, 0.35, 0.23, 0);
  box(g, 0.2, 1.6, 1, 0.9, 0.01, 0.03, palette.glass);
  box(g, 1.2, 1.6, 0.02, 0.9, 0.04, 2, palette.glass, true);
  box(g, 2.45, 0.35, 0.75, 0.85, 0, 1.75, palette.cream);
  for (const y of [0.43, 1.3]) {
    const disk = new THREE.Mesh(
      new THREE.CircleGeometry(0.24, 24),
      material(palette.glass),
    );
    disk.position.set(2.825, y, -1.205);
    disk.rotation.y = Math.PI;
    g.add(disk);
  }
  box(g, 3.28, 0.35, 0.47, 0.7, 0, 0.9, palette.wood);
  bed(u, 0.8, 4.55, 1.35, 1.9, b);
  bed(u, 2.85, 4.55, 1.35, 1.9, b);
  bed(u, 6.65, 6.15, 2, 2, b, true);
  box(u, 0.35, 2.75, 3.05, 0.6, b, 2.25, palette.wood);
  box(u, 3.95, 1.95, 0.6, 0.55, b, 2.25, palette.wood);
  box(u, 0.35, 8.7, 4.3, 0.6, b, 2.25, palette.wood);
  box(u, 0.35, 7.15, 0.6, 1.2, b, 0.8, palette.wood);
  for (const d of [5.57, 8.25])
    box(u, 8.1, d, 0.55, 0.48, b, 0.55, palette.wood);
  vanity(u, 1.65, 0.2, 1.9, b, true, 0.6);
  toilet(u, 2, 1.72, b, true);
  box(u, 0.2, 0.2, 1.1, 2.3, b + 0.01, 0.03, palette.glass);
  for (const [d, depth] of [
    [0.2, 0.68],
    [1.78, 0.72],
  ])
    box(u, 1.3, d, 0.02, depth, b, 2.1, palette.glass, true);

  return {
    setGateOpen(open: boolean) {
      gateLeaf.position.x = open ? gate.travel : 0;
    },
    setDrainageVisible(visible: boolean) {
      drainage.visible = visible;
    },
    setDepthCues(enabled: boolean) {
      depthCuesEnabled = enabled;
    },
    setView(
      view: View,
      walking: boolean,
      showRoof: boolean,
      showFurniture: boolean,
    ) {
      // Wall decomposition edges aid interior navigation, not facade construction joints.
      depthEdges.forEach((edge) => {
        edge.visible = depthCuesEnabled && (walking || view !== "exterior");
      });
      ground.visible = walking || view !== "upper";
      upper.visible = walking || view !== "ground";
      roof.visible = walking || (view === "exterior" && showRoof);
      furniture.ground.visible = showFurniture;
      furniture.upper.visible = showFurniture;
    },
  };
}
