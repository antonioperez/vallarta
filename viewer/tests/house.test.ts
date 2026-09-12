import { describe, it, expect } from 'vitest';
import { rooms, walls, wallSolids, heights, levels, floorAt, canStand, tryMove, roomViewpoints, stair } from '../src/house';

describe('Concept 05 model', () => {
  it('keeps adopted floor and ceiling levels', () => {
    expect(heights.ground_clear).toBe(3);
    expect(levels.upper).toBe(3.4);
    expect(heights.upper_ceiling_level).toBeCloseTo(6.2);
    expect(rooms.filter(r => r.name.includes('bedroom'))).toHaveLength(3);
  });
  it('does not create openings outside their wall or above its ceiling', () => {
    for (const floor of ['ground', 'upper'] as const) for (const wall of walls[floor]) {
      const [x, z, w, d] = wall.rect, start = w > d ? x : z, end = start + Math.max(w, d);
      let previousEnd = start;
      for (const o of [...wall.openings ?? []].sort((a,b) => a.start-b.start)) {
        expect(o.start).toBeGreaterThanOrEqual(previousEnd);
        expect(o.start + o.width).toBeLessThanOrEqual(end);
        expect(o.sill + o.height).toBeLessThanOrEqual(floor === 'ground' ? 3 : 2.8);
        previousEnd = o.start + o.width;
      }
    }
  });
  it('leaves a continuous hall → service passage → bathroom route', () => {
    for (let x = 5; x >= 1.7; x -= .05) expect(canStand(x, 2, 0), `blocked at x=${x}`).toBe(true);
    expect(canStand(3.875, 2.7, 0)).toBe(false);
  });
  it('opens guest room, primary and dressing doors while retaining partitions', () => {
    expect(canStand(3.875, 3.45, 0)).toBe(true);
    expect(canStand(4.875, 3.85, 3.4)).toBe(true);
    expect(canStand(5.5, 4.875, 3.4)).toBe(true);
    expect(canStand(4.875, 7.6, 3.4)).toBe(true);
    expect(canStand(4.875, 5.8, 3.4)).toBe(false);
  });
  it('every room shortcut lands clear of walls on its selected floor', () => {
    for (const room of rooms) {
      const [x, depth] = roomViewpoints[room.id];
      expect(canStand(x, depth, levels[room.floor]), room.id).toBe(true);
      expect(floorAt(x, depth, levels[room.floor]), room.id).toBeCloseTo(levels[room.floor]);
    }
  });
  it('walks all twenty risers, the turn and upper arrival without teleportation', () => {
    let feet = 0;
    const move = (x: number, d: number) => {
      const next = tryMove(x, d, feet);
      expect(next, `blocked at ${x},${d},${feet}`).not.toBeNull(); feet = next!;
    };
    for (let d = 1; d < 4.25; d += .025) move(6.9, d);
    expect(feet).toBeCloseTo(1.7);
    for (let x = 6.9; x < 8.1; x += .025) move(x, 4.25);
    for (let d = 4.25; d > .8; d -= .025) move(8.1, d);
    expect(feet).toBeCloseTo(3.4);
    for (let d = .8; d < 4.25; d += .025) move(8.1, d);
    for (let x = 8.1; x > 6.9; x -= .025) move(x, 4.25);
    for (let d = 4.25; d > .8; d -= .025) move(6.9, d);
    expect(feet).toBe(0);
    expect(stair.risers * stair.riser).toBeCloseTo(3.4);
  });
  it('blocks walking through exterior walls, off the upper floor, or into the void', () => {
    expect(tryMove(0, 3, 0)).toBeNull();
    expect(tryMove(5, 10, 3.4)).toBeNull();
    expect(tryMove(7.51, 2, 3.4)).toBeNull();
    for (const s of wallSolids('ground')) expect(s.top).toBeGreaterThan(s.bottom);
  });
});
