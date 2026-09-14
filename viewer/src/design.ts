import schedule from "../../design/concept-14/area-schedule.json";
import geometry from "../../design/concept-14/rendering-geometry.json";
import style from "../../design/concept-14/selected-style-geometry.json";

export { schedule, geometry, style };
export const kitchen = schedule.kitchen_revision;
export const gate = geometry.gate_lot_coordinates_m;
export const site = geometry.site_lot_coordinates_m;
export type Point = readonly [number, number, number]; // building x, depth, height
export type Rectangle = readonly [number, number, number, number];
export const lotRect = (r: readonly number[]): Rectangle => [
  r[0] - site.building_x,
  r[1] - site.front_depth,
  r[2],
  r[3],
];
export const lotPoint = (p: readonly number[], height: number): Point => [
  p[0] - site.building_x,
  p[1] - site.front_depth,
  height,
];

const [x, d, w, depth] = lotRect(style.roof.footprint_lot);
const eave = style.roof.main_top;
const fl: Point = [x, d, eave],
  fr: Point = [x + w, d, eave];
const rl: Point = [x, d + depth, eave],
  rr: Point = [x + w, d + depth, eave];
const [r1, r2] = style.roof.ridge_lot_xy_start_end.map((p) =>
  lotPoint(p, style.roof.highest_top),
);
// Polygon order follows each eave. Roof tiles run from eave toward ridge.
export const mainRoofFaces: Point[][] = [
  [fl, fr, r1],
  [fr, rr, r2, r1],
  [rr, rl, r2],
  [rl, fl, r1, r2],
];
const [tx, td, tw, tdepth] = lotRect(style.rear_canopy.footprint_lot);
export const terraceRoofFace: Point[] = [
  [tx, td + tdepth, style.rear_canopy.low_top],
  [tx + tw, td + tdepth, style.rear_canopy.low_top],
  [tx + tw, td, style.rear_canopy.high_top],
  [tx, td, style.rear_canopy.high_top],
];

// Diagram centerlines from roof coordination 01. These are NOT pipe/gutter sizes.
export const proposedCollectionPaths: Point[][] = [
  [
    [1.1, 5.55],
    [9.85, 5.55],
    [9.85, 15.55],
    [1.1, 15.55],
    [1.1, 5.55],
  ].map((p) => lotPoint(p, 6.67)),
  [
    [3.05, 19.18],
    [8.9, 19.18],
  ].map((p) => lotPoint(p, 2.78)),
  [
    [4.9, 5.05],
    [6.55, 5.05],
  ].map((p) => lotPoint(p, 2.87)),
];
export const proposedFlowArrows: Point[][] = [
  [lotPoint([5.5, 8.4], 7.55), lotPoint([5.5, 5.8], 6.77)],
  [lotPoint([5.5, 12.6], 7.55), lotPoint([5.5, 15.3], 6.77)],
  [lotPoint([3.2, 10.55], 7.32), lotPoint([1.35, 10.55], 6.77)],
  [lotPoint([7.7, 10.55], 7.32), lotPoint([9.6, 10.55], 6.79)],
  [lotPoint([6, 17.1], 3.44), lotPoint([6, 18.95], 2.89)],
];

// Two equal sliding leaves overlap in the building-right half when open.
export const rearSliderPanelRect: Rectangle = [
  kitchen.rear_slider.parked_x_m[0],
  kitchen.rear_slider.wall_depth_m - 0.025,
  kitchen.rear_slider.parked_x_m[1] - kitchen.rear_slider.parked_x_m[0],
  0.08,
];
