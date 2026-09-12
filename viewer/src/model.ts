import * as THREE from "three";
import {
  heights,
  levels,
  rooms,
  stair,
  wallSolids,
  walls,
  type Floor,
  type View,
} from "./house";

const palette = {
  plaster: "#e6ddcb",
  stone: "#c3b39b",
  tile: "#d1b99b",
  wood: "#9a6545",
  cream: "#f7f0e4",
  sage: "#819080",
  rust: "#a4573e",
  metal: "#394c45",
  glass: "#9fbfc0",
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
) {
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
function tree(parent: THREE.Group, x: number, d: number, size = 1) {
  cylinder(parent, x, d, 0, 0.12 * size, 1.6 * size, palette.wood);
  const crown = new THREE.Mesh(
    new THREE.IcosahedronGeometry(0.8 * size, 2),
    material("#78815a"),
  );
  crown.position.set(x, 2 * size, -d);
  crown.scale.y = 1.2;
  crown.castShadow = true;
  parent.add(crown);
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
      0.8,
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
  roof.name = "Illustrative roof";
  scene.add(site, ground, upper, roof);
  box(site, -1, -5.5, 10, 20, -0.22, 0.2, "#c6beac");
  box(site, -1, 10.5, 10, 4, -0.02, 0.035, "#a1a785");
  box(site, 2, 10.5, 6, 3, 0.015, 0.07, palette.tile);
  box(site, -1, -7.5, 10, 2, -0.25, 0.04, "#a3a39a");
  box(site, -1, -5.5, 10, 0.35, -0.02, 0.06, palette.stone);
  // Site enclosure is illustrative; openings preserve vehicle and pedestrian access.
  for (const x of [-1, 8.9]) box(site, x, -5.5, 0.1, 20, 0, 0.8, palette.stone);
  box(site, -1, 14.4, 10, 0.1, 0, 1.2, palette.stone);
  for (let n = 0; n < 5; n++)
    box(site, 4.32, -5.05 + n * 0.95, 1.08, 0.65, 0.01, 0.055, "#e9e4d8");
  tree(site, 0.25, 13.1, 1.1);
  tree(site, 0.9, 14, 0.8);
  tree(site, 8.4, 13.8, 0.8);
  tree(site, 5.8, -3, 0.7);
  tree(site, 4.1, -4.1, 0.65);
  for (const x of [2.1, 7.8])
    box(site, x, 13.3, 0.14, 0.14, 0.08, 2.65, palette.wood);
  for (let n = 0; n < 13; n++)
    box(site, 2 + n * 0.48, 10.5, 0.1, 3, 2.78, 0.12, palette.wood);
  table(site, 4, 11.5, 0.08);
  // One schematic car to preserve the parking footprint.
  box(site, 0.8, -4.95, 1.85, 4.5, 0.25, 0.55, "#7b8c87");
  box(site, 0.95, -3.9, 1.55, 2.1, 0.8, 0.65, "#a5b9b6");
  for (const x of [0.73, 2.5])
    for (const d of [-4.1, -1.2])
      cylinder(site, x, d, 0.1, 0.28, 0.35, palette.metal);

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
    box(upper, r[0], r[1], r[2], r[3], slabBottom, slabHeight, palette.tile);
  }
  box(roof, 0, 0, 9, 9.5, heights.upper_ceiling_level, 0.18, palette.plaster);
  box(roof, 0, 9.5, 9, 1, 3, 0.18, palette.plaster);
  for (const floor of ["ground", "upper"] as const) {
    const group = floor === "ground" ? ground : upper,
      base = levels[floor];
    for (const s of wallSolids(floor))
      box(group, s.x, s.z, s.w, s.d, s.bottom, s.top - s.bottom);
    for (const wall of walls[floor]) {
      const [x, d, w, depth] = wall.rect,
        horizontal = w > depth;
      for (const o of wall.openings ?? []) {
        if (o.kind !== "window") continue;
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
          palette.glass,
          true,
        );
        if (horizontal) {
          for (const dx of [0, o.width / 2, o.width - 0.025])
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
      box(
        group,
        x,
        d,
        w,
        depth,
        base + 0.002,
        0.007,
        /bathroom/.test(room.name)
          ? "#c9d1c8"
          : /bedroom/.test(room.name)
            ? "#d6c0a1"
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
  box(g, 0.2, 2.85, 0.6, 1.25, 0, 2.25, palette.wood);
  box(g, 5.7, 2.6, 0.45, 1.2, 0, 0.85, palette.wood);
  box(g, 5.2, 4.95, 0.8, 0.72, 0, 1.9, "#afbab4");
  box(g, 6, 4.95, 2.8, 0.65, 0, 0.9, palette.wood);
  box(g, 8.15, 5.6, 0.65, 1.05, 0, 0.9, palette.wood);
  box(g, 6, 4.95, 2.8, 0.65, 0.9, 0.045, palette.cream);
  box(g, 8.15, 5.6, 0.65, 1.05, 0.9, 0.045, palette.cream);
  box(g, 6.35, 5.06, 0.75, 0.43, 0.95, 0.01, palette.metal);
  for (const x of [6.53, 6.89])
    for (const d of [5.17, 5.38])
      cylinder(g, x, d, 0.96, 0.07, 0.006, "#8b9390");
  box(g, 8.25, 5.9, 0.43, 0.65, 0.95, 0.015, palette.glass);
  table(g, 5.5, 7.55, 0);
  box(g, 0.35, 9.25, 3.3, 0.85, 0.1, 0.4, palette.cream);
  box(g, 0.35, 9.94, 3.3, 0.16, 0.5, 0.38, palette.cream);
  box(g, 0.35, 8.05, 0.85, 1.2, 0.1, 0.4, palette.cream);
  box(g, 0.35, 8.05, 0.16, 1.2, 0.5, 0.38, palette.cream);
  box(g, 0.95, 7.9, 2.7, 2.2, 0.012, 0.015, "#b9b39e");
  box(g, 1.6, 8.15, 1.25, 0.55, 0.15, 0.22, palette.wood);
  for (const x of [2, 3]) box(g, x, 7.1, 0.75, 0.75, 0.12, 0.4, palette.sage);
  box(g, 1.95, 6.9, 1.25, 0.12, 0.8, 0.7, palette.metal);
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
  box(u, 0.35, 2.65, 3.05, 0.6, b, 2.25, palette.wood);
  box(u, 3.95, 1.95, 0.6, 0.55, b, 2.25, palette.wood);
  box(u, 0.35, 8.7, 4.3, 0.6, b, 2.25, palette.wood);
  box(u, 0.35, 7.15, 0.6, 1.2, b, 0.8, palette.wood);
  for (const d of [5.57, 8.25])
    box(u, 8.1, d, 0.55, 0.48, b, 0.55, palette.wood);
  vanity(u, 1.65, 0.2, 1.9, b, true);
  toilet(u, 2, 1.72, b, true);
  box(u, 0.2, 0.2, 1.1, 2.3, b + 0.01, 0.03, palette.glass);
  for (const [d, depth] of [
    [0.2, 0.68],
    [1.78, 0.72],
  ])
    box(u, 1.3, d, 0.02, depth, b, 2.1, palette.glass, true);

  return {
    setView(
      view: View,
      walking: boolean,
      showRoof: boolean,
      showFurniture: boolean,
    ) {
      ground.visible = walking || view !== "upper";
      upper.visible = walking || view !== "ground";
      roof.visible = walking || (view === "exterior" && showRoof);
      furniture.ground.visible = showFurniture;
      furniture.upper.visible = showFurniture;
    },
  };
}
