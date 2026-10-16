import * as THREE from "three";
import { registerFinish } from "./materials";

// A subtle, repeating 60 cm ceramic tile texture provides a real scale cue.
// Generated locally so the viewer has no external texture dependencies.
export function tileMaterial(color: string) {
  const canvas = document.createElement("canvas");
  canvas.width = canvas.height = 128;
  const ctx = canvas.getContext("2d")!;
  ctx.fillStyle = color;
  ctx.fillRect(0, 0, 128, 128);
  // Deterministic mottling, not frame-dependent random noise.
  for (let y = 0; y < 128; y += 2)
    for (let x = 0; x < 128; x += 2) {
      ctx.fillStyle = (x * 17 + y * 31) % 13 < 6 ? "#ffffff08" : "#00000005";
      ctx.fillRect(x, y, 2, 2);
    }
  ctx.fillStyle = "#68665855";
  ctx.fillRect(0, 0, 1, 128);
  ctx.fillRect(0, 0, 128, 1);
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(1 / 0.6, 1 / 0.6);
  texture.anisotropy = 4;
  return registerFinish(
    new THREE.MeshStandardMaterial({ map: texture, roughness: 0.85 }),
    "floor",
  );
}

export function addFloorFinish(
  parent: THREE.Group,
  x: number,
  d: number,
  width: number,
  depth: number,
  y: number,
  color: string,
) {
  const geometry = new THREE.PlaneGeometry(width, depth);
  const uv = geometry.getAttribute("uv");
  for (let i = 0; i < uv.count; i++)
    uv.setXY(i, uv.getX(i) * width + x, uv.getY(i) * depth + d);
  const floor = new THREE.Mesh(geometry, tileMaterial(color));
  floor.rotation.x = -Math.PI / 2;
  floor.position.set(x + width / 2, y, -d - depth / 2);
  floor.receiveShadow = true;
  parent.add(floor);
}

const edgeMaterial = new THREE.LineBasicMaterial({
  color: "#394b46",
  transparent: true,
  opacity: 0.22,
  depthWrite: false,
});
const edges = new THREE.EdgesGeometry(new THREE.BoxGeometry(1, 1, 1));
export function addEdges(mesh: THREE.Mesh) {
  const outline = new THREE.LineSegments(edges, edgeMaterial);
  mesh.add(outline);
  return outline;
}
