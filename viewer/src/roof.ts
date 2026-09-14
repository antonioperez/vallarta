import * as THREE from "three";
import type { Point } from "./design";

export const worldPoint = ([x, depth, height]: Point) =>
  new THREE.Vector3(x, height, -depth);

let clay: THREE.MeshStandardMaterial;
function clayMaterial() {
  if (clay) return clay;
  // Illustrative clay profile and laps, generated in the viewer; no product selected.
  const canvas = document.createElement("canvas");
  canvas.width = canvas.height = 128;
  const ctx = canvas.getContext("2d")!;
  const gradient = ctx.createLinearGradient(0, 0, 128, 0);
  gradient.addColorStop(0, "#76402d");
  gradient.addColorStop(0.18, "#bc6844");
  gradient.addColorStop(0.5, "#c67750");
  gradient.addColorStop(0.84, "#985134");
  gradient.addColorStop(1, "#76402d");
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, 128, 128);
  ctx.fillStyle = "#613c2a77";
  ctx.fillRect(0, 0, 128, 5);
  for (let y = 8; y < 128; y += 4)
    for (let x = 0; x < 128; x += 4) {
      ctx.fillStyle = (x * 17 + y * 31) % 13 < 6 ? "#ffffff09" : "#00000008";
      ctx.fillRect(x, y, 3, 3);
    }
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(1 / 0.22, 1 / 0.34);
  texture.anisotropy = 8;
  clay = new THREE.MeshStandardMaterial({
    map: texture,
    roughness: 0.92,
    side: THREE.DoubleSide,
  });
  return clay;
}

export function addClayRoof(
  parent: THREE.Group,
  faces: Point[][],
  thickness: number,
  name: string,
) {
  const group = new THREE.Group();
  group.name = name;
  parent.add(group);
  const soffit = new THREE.MeshStandardMaterial({
    color: "#b59879",
    roughness: 0.9,
    side: THREE.DoubleSide,
  });
  for (const face of faces) {
    const v = face.map(worldPoint),
      uAxis = v[1].clone().sub(v[0]).normalize();
    const normal = v[1]
      .clone()
      .sub(v[0])
      .cross(v[2].clone().sub(v[0]))
      .normalize();
    const vAxis = normal.clone().cross(uAxis).normalize();
    const points: number[] = [],
      uv: number[] = [];
    for (let i = 1; i < v.length - 1; i++)
      for (const index of [0, i, i + 1]) {
        points.push(...v[index].toArray());
        const delta = v[index].clone().sub(v[0]);
        uv.push(delta.dot(uAxis), delta.dot(vAxis));
      }
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute(
      "position",
      new THREE.Float32BufferAttribute(points, 3),
    );
    geometry.setAttribute("uv", new THREE.Float32BufferAttribute(uv, 2));
    geometry.computeVertexNormals();
    const top = new THREE.Mesh(geometry, clayMaterial());
    top.castShadow = true;
    top.receiveShadow = true;
    group.add(top);
    const bottom = new THREE.Mesh(geometry, soffit);
    bottom.position.y = -thickness;
    group.add(bottom);
    // A visual roof edge only. Actual structure/build-up still requires design.
    for (let i = 0; i < v.length; i++) {
      const a = v[i],
        b = v[(i + 1) % v.length],
        a2 = a.clone(),
        b2 = b.clone();
      a2.y -= thickness;
      b2.y -= thickness;
      const edge = new THREE.BufferGeometry().setFromPoints([
        a,
        b,
        a2,
        b,
        b2,
        a2,
      ]);
      edge.computeVertexNormals();
      const mesh = new THREE.Mesh(edge, soffit);
      mesh.castShadow = true;
      group.add(mesh);
    }
  }
  return group;
}
