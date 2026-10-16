import { describe, it, expect, vi } from "vitest";
import { kitchen } from "../src/design";
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

describe("Concept 14 model", () => {
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

describe("Concept 14 acoustic and layout revision", () => {
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

describe("selected exterior and kitchen coordination", () => {
  it("uses one private bathroom ribbon and two separate stair windows at the selected levels", () => {
    const front = walls.upper.find((w) => w.rect[1] === 0 && w.rect[2] > 8)!;
    expect(front.openings).toHaveLength(2);
    const [bath, stairs] = front.openings!;
    expect(bath.width).toBe(3.1);
    expect(bath.sill).toBeCloseTo(1.75);
    expect(bath.height).toBe(0.55);
    expect(bath.privacy).toBe(true);
    expect(bath.modules).toBe(3);
    expect(stairs.sill + levels.upper).toBeCloseTo(4.5);
    expect(stairs.sill + stairs.height).toBeCloseTo(2.6);
  });
  it("renders the measured roof, car, kitchen and complete sliding leaf within their reservations", async () => {
    const THREE = await import("three");
    const { createHouse } = await import("../src/model");
    const { gate, lotRect, geometry } = await import("../src/design");
    // Canvas is used only for procedural material maps; verify the actual scene meshes.
    vi.stubGlobal("document", {
      createElement: () => ({
        width: 128,
        height: 128,
        getContext: () => ({
          fillRect() {},
          createLinearGradient: () => ({ addColorStop() {} }),
        }),
      }),
    });
    try {
      const scene = new THREE.Scene(),
        model = createHouse(scene);
      const bounds = (name: string) =>
        new THREE.Box3().setFromObject(scene.getObjectByName(name)!);
      const roof = bounds("Main hip roof");
      expect(roof.min.x).toBeCloseTo(0);
      expect(roof.max.x).toBeCloseTo(9);
      expect(roof.min.z).toBeCloseTo(-9.85);
      expect(roof.max.z).toBeCloseTo(0.35);
      expect(roof.max.y).toBeCloseTo(7.95);
      const terrace = bounds("Terrace clay roof");
      expect(terrace.min.y).toBeCloseTo(2.5);
      expect(terrace.max.y).toBeCloseTo(3.6);
      expect(terrace.min.z).toBeCloseTo(-13.5);
      expect(
        20 - geometry.adopted.front_court_depth + terrace.min.z,
      ).toBeCloseTo(0.7);
      const car = bounds("4.80 m planning car");
      expect(car.max.z - car.min.z).toBeCloseTo(4.8);
      expect(car.max.x - car.min.x).toBeCloseTo(1.85);
      expect(car.min.z).toBeCloseTo(0.45);
      model.setGateOpen(false);
      const closed = bounds("Complete sliding gate leaf");
      expect(closed.min.z - car.max.z).toBeCloseTo(0.25);
      model.setGateOpen(true);
      const opened = bounds("Complete sliding gate leaf");
      expect(opened.min.x - closed.min.x).toBeCloseTo(3.8);
      const [rx, rd, rw, rdepth] = lotRect(gate.runback_reserve);
      expect(opened.min.x).toBeGreaterThanOrEqual(rx);
      expect(opened.max.x).toBeLessThanOrEqual(rx + rw);
      expect(-opened.max.z).toBeGreaterThanOrEqual(rd);
      expect(-opened.min.z).toBeLessThanOrEqual(rd + rdepth);
      expect(opened.min.x).toBeGreaterThan(gate.opening_x[1] - 1);
      const counter = bounds("3.60 m kitchen counter"),
        sink = bounds("Sink"),
        cooktop = bounds("Cooktop"),
        fridge = bounds("Right-wall refrigerator");
      expect(counter.max.x - counter.min.x).toBeCloseTo(3.6);
      expect(counter.min.x).toBeCloseTo(5.2);
      expect(sink.min.x - cooktop.max.x).toBeCloseTo(0.65);
      expect(fridge.min.x).toBeCloseTo(8.03);
      expect(fridge.max.x).toBeLessThan(8.8);
      expect(-fridge.min.z).toBeCloseTo(7.65);
      const rect = (b: InstanceType<typeof THREE.Box3>) => [
        b.min.x,
        -b.max.z,
        b.max.x - b.min.x,
        b.max.z - b.min.z,
      ];
      const overlaps = (a: number[], b: number[]) =>
        Math.min(a[0] + a[2], b[0] + b[2]) - Math.max(a[0], b[0]) > 1e-6 &&
        Math.min(a[1] + a[3], b[1] + b[3]) - Math.max(a[1], b[1]) > 1e-6;
      const ret = bounds("Kitchen right-wall return"),
        wall = bounds("Kitchen backing wall extension"),
        dining = bounds("Six-seat indoor table"),
        panels = bounds("Rear slider parked panels");
      const upperCabinets = bounds("Kitchen wall cabinets");
      // Wall units remain over the worktop, clear of the cooktop and below the ceiling.
      expect(upperCabinets.min.x).toBeGreaterThan(cooktop.max.x);
      expect(upperCabinets.max.x).toBeLessThanOrEqual(counter.max.x);
      expect(upperCabinets.max.z).toBeCloseTo(counter.max.z);
      expect(upperCabinets.min.z).toBeGreaterThan(counter.min.z);
      expect(upperCabinets.min.y - counter.max.y).toBeGreaterThan(0.6);
      expect(upperCabinets.max.y).toBeLessThan(3);
      for (const cabinet of [counter, ret, upperCabinets]) {
        expect(overlaps(rect(cabinet), kitchen.rectangles_m.through_route)).toBe(false);
        expect(overlaps(rect(cabinet), kitchen.fridge_door.sweep_bounds)).toBe(false);
      }
      rect(ret).forEach((n, i) =>
        expect(n).toBeCloseTo([8.15, 5.6, 0.65, 1.05][i]),
      );
      expect(wall.min.x).toBeCloseTo(counter.min.x);
      expect(wall.max.x).toBeCloseTo(6.3);
      expect(wall.max.y).toBeCloseTo(3);
      expect(wall.min.z).toBeCloseTo(counter.max.z);
      expect(dining.max.x - dining.min.x).toBeCloseTo(0.9);
      expect(dining.max.z - dining.min.z).toBeCloseTo(1.8);
      expect(fridge.min.x - dining.max.x).toBeCloseTo(1.13);
      expect(panels.min.x).toBeCloseTo(6.5);
      expect(panels.max.x).toBeCloseTo(8.1);
      expect(panels.max.y).toBeCloseTo(2.5);
      const chairs: InstanceType<typeof THREE.Object3D>[] = [];
      scene.traverse((o) => {
        if (/^Indoor dining chair \d+$/.test(o.name)) chairs.push(o);
      });
      expect(chairs).toHaveLength(6);
      const obstacles = [
        rect(counter),
        rect(ret),
        rect(fridge),
        rect(dining),
        rect(wall),
        kitchen.fridge_door.sweep_bounds,
      ];
      for (const [i, chair] of chairs.entries()) {
        const actual = rect(new THREE.Box3().setFromObject(chair));
        actual.forEach((n, j) =>
          expect(n).toBeCloseTo(kitchen.dining_chairs_drawn_m[i][j]),
        );
        // Sample the complete outward movement, not only its endpoints.
        for (let step = 0; step <= 30; step++) {
          const moved = [...actual],
            [vx, vd] = kitchen.chair_outward_vectors[i];
          moved[0] += (vx * step) / 100;
          moved[1] += (vd * step) / 100;
          for (const other of [
            ...obstacles,
            kitchen.rectangles_m.through_route,
            kitchen.rear_turn_route_m,
          ])
            expect(overlaps(moved, other), `${chair.name} at ${step} cm`).toBe(
              false,
            );
          expect(moved[1] + moved[3]).toBeLessThanOrEqual(10.3 + 1e-6);
        }
      }
      const frontChair = rect(new THREE.Box3().setFromObject(chairs[4]));
      expect(frontChair[1] - 0.3 - -counter.min.z).toBeCloseTo(1.15);
      // Sweep follows the actual appliance face and retained dining-end hinge.
      const hinge = [fridge.min.x, -fridge.min.z],
        leafWidth = fridge.max.z - fridge.min.z;
      hinge.forEach((n, i) =>
        expect(n).toBeCloseTo(kitchen.fridge_door.hinge[i]),
      );
      expect(leafWidth).toBeCloseTo(kitchen.fridge_door.width);
      for (let angle = 0; angle <= 90; angle++) {
        const a = (angle * Math.PI) / 180;
        const leaf = [
          hinge[0] - Math.sin(a) * leafWidth,
          hinge[1] - Math.cos(a) * leafWidth,
          Math.sin(a) * leafWidth,
          Math.cos(a) * leafWidth,
        ];
        for (const other of [
          rect(counter),
          rect(ret),
          rect(dining),
          kitchen.rectangles_m.sink_standing,
          ...kitchen.dining_chairs_drawn_m,
          ...kitchen.dining_chairs_pulled_m,
        ])
          expect(overlaps(leaf, other), `door at ${angle} degrees`).toBe(false);
      }
      model.setDrainageVisible(true);
      expect(scene.getObjectByName("Proposed drainage diagram")!.visible).toBe(
        true,
      );
      model.setView("ground", false, true, true);
      expect(
        scene.getObjectByName("Selected clay roofs and canopies")!.visible,
      ).toBe(false);
      model.setView("upper", true, false, true);
      expect(
        scene.getObjectByName("Selected clay roofs and canopies")!.visible,
      ).toBe(true);
    } finally {
      vi.unstubAllGlobals();
    }
  });
});

describe("Concept 14 kitchen circulation", () => {
  it("blocks the new full-height backing and parked glazing, with a continuous left terrace route", () => {
    expect(canStand(5.7, 4.87, 0)).toBe(false);
    expect(canStand(5.7, 4.87, 2.7)).toBe(false);
    for (let d = 4.3; d <= 9.8; d += 0.025) expect(tryMove(4.45, d, 0)).toBe(0);
    for (let x = 4.45; x <= 5.45; x += 0.025)
      expect(tryMove(x, 9.8, 0)).toBe(0);
    for (let d = 9.8; d <= 11; d += 0.025) expect(tryMove(5.45, d, 0)).toBe(0);
    expect(tryMove(7.3, 10.4, 0)).toBeNull();
    expect(tryMove(5.45, 10.4, 0)).toBe(0);
  });
});
