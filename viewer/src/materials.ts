import * as THREE from "three";

export type Finish =
  | "plaster"
  | "wood"
  | "fabric"
  | "floor"
  | "clay"
  | "ceramic"
  | "metal"
  | "glass";
type Maps = {
  map?: THREE.Texture;
  normalMap?: THREE.Texture;
  roughnessMap?: THREE.Texture;
};
const profiles = {
  plaster: {
    size: [2, 2],
    normal: 0.16,
    roughness: 0.9,
    maps: ["normal", "roughness"],
  },
  wood: {
    size: [1.2, 1.2],
    normal: 0.3,
    roughness: 0.65,
    maps: ["color", "normal", "roughness"],
  },
  fabric: {
    size: [0.35, 0.35],
    normal: 0.45,
    roughness: 1,
    maps: ["normal", "roughness"],
  },
  floor: {
    size: [2.4, 2.4],
    normal: 0.3,
    roughness: 0.65,
    maps: ["color", "normal", "roughness"],
  },
  clay: {
    size: [2.64, 1.7],
    normal: 0.8,
    roughness: 0.95,
    maps: ["color", "normal", "roughness"],
  },
} as const;
type TexturedFinish = keyof typeof profiles;
const loaded = new Map<Finish, Maps>();
const records: Array<{
  material: THREE.MeshStandardMaterial;
  finish: Finish;
  base: {
    color: THREE.Color;
    roughness: number;
    metalness: number;
    map: THREE.Texture | null;
  };
}> = [];
let enabled = true;
let loadGeneration = 0;

function update(record: (typeof records)[number]) {
  const { material: m, finish, base } = record;
  m.color.copy(base.color);
  m.roughness = base.roughness;
  m.metalness = base.metalness;
  m.map = base.map;
  m.normalMap = m.roughnessMap = null;
  if (enabled) {
    const maps = loaded.get(finish);
    if (maps) {
      const profile = profiles[finish as TexturedFinish];
      m.map = maps.map ?? base.map;
      m.normalMap = maps.normalMap ?? null;
      m.roughnessMap = maps.roughnessMap ?? null;
      m.normalScale.setScalar(profile.normal);
      m.roughness = profile.roughness;
      if (finish === "wood" || finish === "clay") m.color.set("#ffffff");
      if (finish === "floor") m.color.set("#f2e7d6");
    }
    if (finish === "ceramic") m.roughness = 0.2;
    if (finish === "metal") {
      m.metalness = 0.82;
      m.roughness = 0.32;
    }
    if (finish === "glass") {
      m.roughness = 0.08;
      m.metalness = 0.15;
    }
  }
  m.needsUpdate = true;
}

// Retain the exact simple material for the comparison switch and load failures.
export function registerFinish(
  material: THREE.MeshStandardMaterial,
  finish: Finish,
) {
  material.userData.finish = finish;
  const record = {
    material,
    finish,
    base: {
      color: material.color.clone(),
      roughness: material.roughness,
      metalness: material.metalness,
      map: material.map,
    },
  };
  records.push(record);
  update(record);
  return material;
}

export function setRealisticMaterials(value: boolean) {
  if (enabled === value) return;
  enabled = value;
  records.forEach(update);
}

// Assets are self-hosted. Failed sets leave their original materials intact.
export async function loadMaterialTextures(maxAnisotropy: number) {
  const generation = ++loadGeneration;
  const loader = new THREE.TextureLoader();
  const results = await Promise.allSettled(
    Object.entries(profiles).map(async ([name, profile]) => {
      const textures: THREE.Texture[] = [];
      const maps: Maps = {};
      const results = await Promise.allSettled(
        profile.maps.map(async (kind) => {
          const texture = await loader.loadAsync(
            `${import.meta.env.BASE_URL}textures/${name}-${kind}.jpg`,
          );
          textures.push(texture);
          texture.colorSpace =
            kind === "color" ? THREE.SRGBColorSpace : THREE.NoColorSpace;
          texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
          texture.repeat.set(1 / profile.size[0], 1 / profile.size[1]);
          texture.anisotropy = Math.min(maxAnisotropy, 4);
          maps[
            kind === "color"
              ? "map"
              : kind === "normal"
                ? "normalMap"
                : "roughnessMap"
          ] = texture;
        }),
      );
      if (
        generation !== loadGeneration ||
        results.some((result) => result.status === "rejected")
      ) {
        textures.forEach((texture) => texture.dispose());
        throw new Error(`Could not load ${name} textures`);
      }
      loaded.set(name as Finish, maps);
      records.filter((r) => r.finish === name).forEach(update);
    }),
  );
  return results.every((result) => result.status === "fulfilled");
}

// Unit-sized meshes still keep their measured bounds; UVs use meters on each face.
const boxes = new Map<string, THREE.BoxGeometry>();
export function texturedBoxGeometry(
  width: number,
  height: number,
  depth: number,
) {
  const key = `${width},${height},${depth}`;
  if (!boxes.has(key)) {
    const geometry = new THREE.BoxGeometry(1, 1, 1);
    const uv = geometry.getAttribute("uv");
    const sizes = [
      [depth, height],
      [depth, height],
      [width, depth],
      [width, depth],
      [width, height],
      [width, height],
    ];
    for (let face = 0; face < 6; face++)
      for (let vertex = 0; vertex < 4; vertex++) {
        const i = face * 4 + vertex;
        uv.setXY(i, uv.getX(i) * sizes[face][0], uv.getY(i) * sizes[face][1]);
      }
    boxes.set(key, geometry);
  }
  return boxes.get(key)!;
}

export function disposeMaterialTextures() {
  loadGeneration++;
  for (const maps of loaded.values())
    for (const texture of Object.values(maps)) texture?.dispose();
  loaded.clear();
}
