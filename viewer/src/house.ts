import schedule from "../../design/concept-06/area-schedule.json";

export type Floor = "ground" | "upper";
export type View = "exterior" | Floor;
export type Rect = readonly [number, number, number, number];
export interface Solid {
  x: number;
  z: number;
  w: number;
  d: number;
  bottom: number;
  top: number;
  floor: Floor;
  lining?: boolean;
}
export interface Opening {
  start: number;
  width: number;
  sill: number;
  height: number;
  kind: "door" | "window";
}
export interface Wall {
  rect: Rect;
  lining?: boolean;
  openings?: Opening[];
}
export const heights = schedule.heights_m;
export const stair = schedule.stair_design;
export const rooms = schedule.rooms.map((room) => ({
  ...room,
  floor: (room.floor === "Ground" ? "ground" : "upper") as Floor,
}));
export const levels = { ground: 0, upper: heights.floor_to_floor };
export const areas = schedule.areas;
export const acoustic = schedule.acoustic_design;
export const livingFurniture = acoustic.living_furniture_m;
const doors = acoustic.doors;
export const openDoorLeaves: Rect[] = [
  [doors.D0_front.x, doors.D0_front.y, 0.045, doors.D0_front.width],
  [
    doors.D1_stair.x - doors.D1_stair.width,
    doors.D1_stair.y,
    doors.D1_stair.width,
    0.045,
  ],
  [
    doors.D2_service.x,
    doors.D2_service.y + doors.D2_service.width - 0.045,
    doors.D2_service.width,
    0.045,
  ],
];
const door = (start: number, width: number): Opening => ({
  start,
  width,
  sill: 0,
  height: 2.2,
  kind: "door",
});
const windowAt = (start: number, width: number, sill = 1): Opening => ({
  start,
  width,
  sill,
  height: 1.3,
  kind: "window",
});

// Rectangles use the original building-local plan coordinates. Doors and windows
// use absolute distance along a wall, not offsets from its start.
export const walls: Record<Floor, Wall[]> = {
  ground: [
    { rect: [0, 0, 0.2, 10.5], openings: [windowAt(4.25, 1.3)] },
    { rect: [8.8, 0, 0.2, 10.5] },
    {
      rect: [0.2, 0, 8.6, 0.2],
      openings: [
        windowAt(0.4, 0.85, 1.5),
        windowAt(3.25, 0.45),
        door(doors.D0_front.x, doors.D0_front.width),
        windowAt(6.8, 1.65),
      ],
    },
    {
      rect: [0.2, 10.3, 8.6, 0.2],
      openings: [windowAt(0.65, 2.9), door(4.9, 3.2)],
    },
    { rect: [6.15, 0.2, 0.15, 4.6], openings: [door(0.25, 0.9)] },
    { rect: [6.3, 4.8, 2.5, 0.15] },
    {
      rect: [3.8, 0.2, 0.15, 6.55],
      openings: [
        door(doors.D2_service.y, doors.D2_service.width),
        door(3, 0.9),
      ],
    },
    { rect: [0.2, 2.5, 3.6, 0.15] },
    { rect: [0.2, 6.75, 3.6, 0.15] },
    { rect: [2.2, 0.2, 0.15, 2.3], openings: [door(1.6, 0.85)] },
  ],
  upper: [
    {
      rect: [0, 0, 0.2, 9.5],
      openings: [windowAt(4.1, 1.5), windowAt(7.8, 0.55)],
    },
    { rect: [8.8, 0, 0.2, 9.5] },
    {
      rect: [0.2, 0, 8.6, 0.2],
      openings: [
        windowAt(0.4, 0.7, 1.4),
        windowAt(2.6, 0.9, 1.4),
        windowAt(6.8, 1.65),
      ],
    },
    { rect: [0.2, 9.3, 8.6, 0.2], openings: [windowAt(5.2, 3.05)] },
    { rect: [6.15, 0.2, 0.15, 4.6], openings: [door(0.25, 0.9)] },
    { rect: [6.3, 4.8, 2.5, 0.15] },
    { rect: [3.8, 0.2, 0.15, 2.3], openings: [door(0.85, 0.9)] },
    { rect: [0.2, 2.5, 4.6, 0.15] },
    {
      rect: [4.8, 2.65, 0.15, 6.65],
      openings: [door(3.4, 0.9), door(7.15, 0.9)],
    },
    { rect: [0.2, 6.75, 4.6, 0.15] },
    { rect: [4.95, 4.8, 3.85, 0.15], openings: [door(5.05, 0.9)] },
  ],
};

// Acoustic lining reservations physically reduce the bedroom envelopes.
for (const floor of ["ground", "upper"] as const) {
  const linings = acoustic.linings_m[floor === "ground" ? "Ground" : "Upper"];
  for (const [x, z, w, d] of linings) {
    let openings: Opening[] = [];
    if (floor === "ground" && x === 3.7) openings = [door(3, 0.9)];
    if (floor === "upper" && x === 4.7) openings = [door(3.4, 0.9)];
    if (floor === "upper" && z === 4.95) openings = [door(5.05, 0.9)];
    walls[floor].push({ rect: [x, z, w, d], openings, lining: true });
  }
}

export function wallSolids(floor: Floor): Solid[] {
  const base = levels[floor],
    height = floor === "ground" ? heights.ground_clear : heights.upper_clear;
  return walls[floor].flatMap(
    ({ rect: [x, z, w, d], openings = [], lining }) => {
      const horizontal = w > d;
      const start = horizontal ? x : z,
        end = start + (horizontal ? w : d);
      const result: Solid[] = [];
      const add = (a: number, b: number, bottom: number, top: number) => {
        if (b - a < 0.0001 || top - bottom < 0.0001) return;
        result.push({
          x: horizontal ? a : x,
          z: horizontal ? z : a,
          w: horizontal ? b - a : w,
          d: horizontal ? d : b - a,
          bottom: base + bottom,
          top: base + top,
          floor,
          lining,
        });
      };
      let cursor = start;
      for (const o of [...openings].sort((a, b) => a.start - b.start)) {
        add(cursor, o.start, 0, height);
        add(o.start, o.start + o.width, 0, o.sill);
        add(o.start, o.start + o.width, o.sill + o.height, height);
        cursor = o.start + o.width;
      }
      add(cursor, end, 0, height);
      return result;
    },
  );
}
export const solids: Solid[] = [
  ...wallSolids("ground"),
  ...wallSolids("upper"),
  ...openDoorLeaves.map(([x, z, w, d]) => ({
    x,
    z,
    w,
    d,
    bottom: 0,
    top: 2.2,
    floor: "ground" as const,
  })),
];
export function inside(x: number, depth: number, rect: Rect, inset = 0) {
  return (
    x >= rect[0] + inset &&
    x <= rect[0] + rect[2] - inset &&
    depth >= rect[1] + inset &&
    depth <= rect[1] + rect[3] - inset
  );
}
export const stairVoid: Rect = [
  6.4,
  stair.start_y,
  stair.opening_width,
  stair.opening_depth,
];
// A low-detail walk surface follows the same 20 risers as the source plan.
// No gravity simulation: attempts to step into unsupported voids are blocked.
export function floorAt(
  x: number,
  depth: number,
  currentFeet: number,
): number | null {
  if (inside(x, depth, [6.4, stair.flight_back_y, 2.25, stair.turn_landing]))
    return stair.midlanding_level;
  if (inside(x, depth, [6.4, stair.start_y, stair.flight_width, stair.run])) {
    return (
      Math.min(9, Math.floor((depth - stair.start_y) / stair.tread) + 1) *
      stair.riser
    );
  }
  if (inside(x, depth, [7.6, stair.start_y, stair.flight_width, stair.run])) {
    return (
      heights.floor_to_floor -
      Math.min(9, Math.floor((depth - stair.start_y) / stair.tread) + 1) *
        stair.riser
    );
  }
  if (inside(x, depth, stairVoid)) return null;
  if (currentFeet > 2.5)
    return inside(x, depth, [0.2, 0.2, 8.6, 9.1]) ? levels.upper : null;
  return inside(x, depth, [-0.8, -5.3, 9.6, 19.6]) ? 0 : null;
}
export function canStand(
  x: number,
  depth: number,
  feet: number,
  radius = 0.17,
): boolean {
  return !solids.some(
    (s) =>
      feet + 1.7 > s.bottom + 0.03 &&
      feet + 0.1 < s.top &&
      x + radius > s.x &&
      x - radius < s.x + s.w &&
      depth + radius > s.z &&
      depth - radius < s.z + s.d,
  );
}
export function tryMove(x: number, depth: number, feet: number) {
  const next = floorAt(x, depth, feet);
  return next !== null &&
    Math.abs(next - feet) <= 0.22 &&
    canStand(x, depth, next)
    ? next
    : null;
}

// Safe viewpoints avoid the schematic furniture and are inside their source rooms.
export const roomViewpoints: Record<string, [number, number, number]> = {
  G1: [2, 3.5, 0],
  G2: [1.65, 1.2, 2.6],
  G3: [3.35, 1.3, Math.PI],
  G4: [7.3, 6.2, 2.8],
  G5: [4.4, 9.7, 2.0],
  G6: [5.1, 2, 0],
  G7: [6.9, 0.7, 0],
  G8: [3.1, 2, Math.PI],
  U1: [2.5, 3.6, 0],
  U2: [2.8, 1.25, 1.5],
  U3: [4.4, 1.45, 0],
  U4: [2.5, 7.7, 0],
  U5: [5.65, 5.7, -0.8],
  U6: [5.5, 2.8, 0],
  U7: [8, 0.7, 0],
};
