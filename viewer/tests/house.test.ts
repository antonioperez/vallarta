import { describe, it, expect } from "vitest";
import {
  rooms,
  walls,
  wallSolids,
  heights,
  levels,
  floorAt,
  canStand,
  tryMove,
  roomViewpoints,
  stair,
  acoustic,
  livingFurniture,
} from "../src/house";

describe("Concept 06 model", () => {
  it("keeps adopted floor and ceiling levels", () => {
    expect(heights.ground_clear).toBe(3);
    expect(levels.upper).toBe(3.4);
    expect(heights.upper_ceiling_level).toBeCloseTo(6.2);
    expect(rooms.filter((r) => r.name.includes("bedroom"))).toHaveLength(3);
  });
  it("does not create openings outside their wall or above its ceiling", () => {
    for (const floor of ["ground", "upper"] as const)
      for (const wall of walls[floor]) {
        const [x, z, w, d] = wall.rect,
          start = w > d ? x : z,
          end = start + Math.max(w, d);
        let previousEnd = start;
        for (const o of [...(wall.openings ?? [])].sort(
          (a, b) => a.start - b.start,
        )) {
          expect(o.start).toBeGreaterThanOrEqual(previousEnd);
          expect(o.start + o.width).toBeLessThanOrEqual(end);
          expect(o.sill + o.height).toBeLessThanOrEqual(
            floor === "ground" ? 3 : 2.8,
          );
          previousEnd = o.start + o.width;
        }
      }
  });
  it("leaves a continuous hall → service passage → bathroom route", () => {
    for (let x = 5; x >= 1.7; x -= 0.05)
      expect(canStand(x, 2, 0), `blocked at x=${x}`).toBe(true);
    expect(canStand(3.875, 2.7, 0)).toBe(false);
  });
  it("opens guest room, primary and dressing doors while retaining partitions", () => {
    expect(canStand(3.875, 3.45, 0)).toBe(true);
    expect(canStand(4.875, 3.85, 3.4)).toBe(true);
    expect(canStand(5.5, 4.875, 3.4)).toBe(true);
    expect(canStand(4.875, 7.6, 3.4)).toBe(true);
    expect(canStand(4.875, 5.8, 3.4)).toBe(false);
  });
  it("every room shortcut lands clear of walls on its selected floor", () => {
    for (const room of rooms) {
      const [x, depth] = roomViewpoints[room.id];
      expect(canStand(x, depth, levels[room.floor]), room.id).toBe(true);
      expect(floorAt(x, depth, levels[room.floor]), room.id).toBeCloseTo(
        levels[room.floor],
      );
    }
  });
  it("walks all twenty risers, the turn and upper arrival without teleportation", () => {
    let feet = 0;
    const move = (x: number, d: number) => {
      const next = tryMove(x, d, feet);
      expect(next, `blocked at ${x},${d},${feet}`).not.toBeNull();
      feet = next!;
    };
    for (let d = 1; d < 4.25; d += 0.025) move(6.9, d);
    expect(feet).toBeCloseTo(1.7);
    for (let x = 6.9; x < 8.1; x += 0.025) move(x, 4.25);
    for (let d = 4.25; d > 0.8; d -= 0.025) move(8.1, d);
    expect(feet).toBeCloseTo(3.4);
    for (let d = 0.8; d < 4.25; d += 0.025) move(8.1, d);
    for (let x = 8.1; x > 6.9; x -= 0.025) move(x, 4.25);
    for (let d = 4.25; d > 0.8; d -= 0.025) move(6.9, d);
    expect(feet).toBe(0);
    expect(stair.risers * stair.riser).toBeCloseTo(3.4);
  });
  it("blocks walking through exterior walls, off the upper floor, or into the void", () => {
    expect(tryMove(0, 3, 0)).toBeNull();
    expect(tryMove(5, 10, 3.4)).toBeNull();
    expect(tryMove(7.51, 2, 3.4)).toBeNull();
    for (const s of wallSolids("ground"))
      expect(s.top).toBeGreaterThan(s.bottom);
  });
});

describe("Concept 06 acoustic and layout revision", () => {
  it("deducts the lining reservations from bedroom dimensions and collision space", () => {
    expect(rooms.find((r) => r.id === "G1")!.area).toBeCloseTo(13.65);
    expect(rooms.find((r) => r.id === "U1")!.area).toBeCloseTo(18);
    expect(rooms.find((r) => r.id === "U5")!.area).toBeCloseTo(16.3625);
    expect(canStand(3.65, 4.3, 0, 0.08)).toBe(false);
    expect(canStand(4.65, 4.4, 3.4, 0.08)).toBe(false);
    expect(canStand(6.3, 5, 3.4, 0.08)).toBe(false);
    expect(canStand(3.75, 3.45, 0, 0.08)).toBe(true);
    expect(canStand(4.75, 3.85, 3.4, 0.08)).toBe(true);
    expect(canStand(5.5, 5, 3.4, 0.08)).toBe(true);
  });
  it("moves the entry and uses a 0.90 m service opening with open door leaves", () => {
    expect(
      walls.ground[2].openings!.find((o) => o.kind === "door")!.start,
    ).toBe(4.1);
    const service = walls.ground.find((w) => w.rect[0] === 3.8)!;
    expect(service.openings![0].width).toBe(0.9);
    expect(service.openings![0].start).toBe(1.55);
    expect(canStand(4.1, 0.7, 0, 0.05)).toBe(false);
    expect(canStand(4.7, 0.7, 0, 0.05)).toBe(true);
    expect(canStand(5.7, 0.27, 0, 0.05)).toBe(false);
    expect(canStand(4.4, 2.43, 0, 0.05)).toBe(false);
  });
  it("puts the TV on the exterior wall and preserves the living aisle", () => {
    expect(livingFurniture.tv).toEqual([0.2, 7.9, 0.08, 1.25]);
    expect(livingFurniture.sofa).toEqual([2.95, 7.25, 0.85, 2.6]);
    const [x, z, w, d] = acoustic.living_route_m;
    for (const r of Object.values(livingFurniture)) {
      const overlap =
        Math.min(x + w, r[0] + r[2]) - Math.max(x, r[0]) > 0 &&
        Math.min(z + d, r[1] + r[3]) - Math.max(z, r[1]) > 0;
      expect(overlap).toBe(false);
    }
  });
});
