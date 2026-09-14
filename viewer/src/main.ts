import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import {
  rooms,
  roomViewpoints,
  levels,
  areas,
  wallSolids,
  tryMove,
  type View,
  type Floor,
} from "./house";
import { createHouse } from "./model";
import "./style.css";
import { createDepthRenderer } from "./depth";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";
import {
  loadMaterialTextures,
  setRealisticMaterials,
  disposeMaterialTextures,
} from "./materials";

const squareFeet = (squareMeters: number) =>
  (squareMeters / 0.3048 ** 2).toLocaleString("en-US", {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  });

const icon = {
  orbit:
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><ellipse cx="12" cy="12" rx="10" ry="4" transform="rotate(-30 12 12)"/><ellipse cx="12" cy="12" rx="4" ry="10" transform="rotate(-30 12 12)"/><circle cx="12" cy="12" r="2" fill="currentColor"/></svg>',
  walk: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><circle cx="14" cy="4" r="2"/><path d="m10 21 3-7-3-4 2-3 3 5 4 1M5 13l3-4 4-2M14 15l3 6"/></svg>',
  reset:
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M4 10a8 8 0 1 1 0 5M4 4v6h6"/></svg>',
  expand:
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M9 3H3v6m12-6h6v6M3 15v6h6m12-6v6h-6"/></svg>',
};
const app = document.querySelector<HTMLDivElement>("#app")!;
app.innerHTML = `
  <header class="masthead"><a class="brand" href="./" aria-label="Las Juntas home"><span class="brand-symbol">lj<span>·</span></span><span>LAS JUNTAS<small>A house in the making</small></span></a><div class="edition"><span class="status-dot"></span> CONCEPT 14 <span class="edition-date">/ SEPTEMBER 2026</span></div></header>
  <main>
    <aside class="sidebar" aria-label="House controls">
      <div class="intro"><p class="eyebrow">THE HOUSE STUDY</p><h1>A little closer<br>to being here.</h1><p class="intro-copy">Step inside the plan. Explore the spaces, the proportions, and how it all connects.</p></div>
      <div class="floor-heading"><h2>Choose your view</h2><span>01 — 03</span></div>
      <div class="floors" aria-label="Floor views"><button data-view="exterior" aria-pressed="true"><span>01</span> Exterior <span>↗</span></button><button data-view="ground" aria-pressed="false"><span>02</span> Ground floor <span>↗</span></button><button data-view="upper" aria-pressed="false"><span>03</span> Upper floor <span>↗</span></button></div>
      <div class="map-section"><div class="floor-heading"><h2 id="map-title">Ground floor</h2><span class="map-caption">ROOM SHORTCUTS</span></div><svg id="minimap" viewBox="-.5 -.5 10 11.5" role="group" aria-label="Floor plan room shortcuts"></svg><p class="map-hint">Select a room to step inside.</p></div>
      <div class="room-select"><label for="room">Jump to a space</label><select id="room"><option value="">Choose a room…</option>${(
        ["ground", "upper"] as const
      )
        .map(
          (f) =>
            `<optgroup label="${f === "ground" ? "Ground floor" : "Upper floor"}">${rooms
              .filter((r) => r.floor === f && !["U3", "G3"].includes(r.id))
              .map(
                (r) => `<option value="${r.id}">${r.id} · ${r.name}</option>`,
              )
              .join("")}</optgroup>`,
        )
        .join("")}</select></div>
      <div class="options"><label><input type="checkbox" id="furniture" checked><span>Furniture</span></label><label><input type="checkbox" id="roof" checked><span>Exterior roof</span></label><label><input type="checkbox" id="depth" checked><span>Depth cues</span></label><label><input type="checkbox" id="gate" checked><span>Vehicle gate open</span></label><label><input type="checkbox" id="drainage"><span>Proposed drainage</span></label><label><input type="checkbox" id="materials" checked><span>Realistic materials</span></label></div>
      <p id="material-status" class="map-hint" role="status">Loading finishes…</p>
      <details class="notes"><summary>About this model <span>+</span></summary><p>Concept 14: A’s windows with B’s clay roofs. Ground clear height 3.00 m (9.84 ft); upper 2.80 m (9.19 ft); floor-to-floor 3.40 m (11.15 ft). Main eave 6.60 m (21.65 ft), ridge 7.95 m (26.08 ft). The 4.80 m car fits the 5.80 m court with the complete sliding gate retracted beside it.</p><p>Drainage lines show proposed collection paths. The inset boundary gutter, pipe sizes, rear transfer and site outfall need design; resolving the gutter may change the roof edge. Blue marks primary paths, orange the boundary/overflow relationships.</p><p>Realistic materials add wood grain, plaster detail, woven upholstery, stone flooring and clay tiles. Switch them off for simpler surfaces. Texture scans: <a href="https://polyhaven.com/" target="_blank" rel="noopener noreferrer">Poly Haven</a> (CC0). Finishes and reflections are illustrative.</p><p>The L-shaped kitchen has a full-height backing wall and the fridge moved toward a six-seat table. G4/G5 are reference subzones; the fridge extends into the dining allocation. The rear slider opens on the left, with panels parked right. The terrace table still seats eight. Obscure bathroom glass is represented as opaque; final glazing and operation remain unresolved. Furniture, gate height and roof build-up are illustrative. Movement collides with walls, interior door leaves and parked rear glazing, not furniture or site gates. Structure, stair headroom and cost remain unverified.</p></details>
      <div class="sidebar-footer">10 × 20 m lot <span>·</span> Las Juntas, México</div>
    </aside>
    <section class="viewport" aria-label="Interactive 3D house">
      <div id="scene" tabindex="0" aria-label="3D model. In walk mode use W A S D or arrow keys to move, drag to look, Escape to return to orbit."></div>
      <div class="scene-top"><div class="scene-title"><span class="eyebrow" id="view-label">01 / EXTERIOR</span><h2 id="scene-heading">The whole picture.</h2></div><div class="utilities"><button id="rear" class="angle-button" aria-label="Show rear exterior">Rear view</button><button id="reset" class="icon-button" aria-label="Reset camera" title="Reset camera">${icon.reset}</button><button id="fullscreen" class="icon-button" aria-label="Toggle fullscreen" title="Fullscreen">${icon.expand}</button></div></div>
      <div class="mode-switch" aria-label="Navigation mode"><button id="orbit" aria-pressed="true">${icon.orbit} Orbit</button><button id="walk" aria-pressed="false">${icon.walk} Walk inside</button></div>
      <div id="crosshair" hidden>+</div><div id="drainage-legend" hidden>PROPOSED DRAINAGE<br><span>Blue: collection paths · Orange: boundary / overflow<br>Diagram lines only; sizes and outfall unresolved.</span></div>
      <div class="view-badge"><span class="status-dot"></span><span id="view-status" role="status" aria-live="polite">Exterior · orbit view</span></div>
      <div class="touch-controls" id="touch-controls" hidden aria-label="Walk controls"><button data-move="forward" aria-label="Move forward">↑</button><div><button data-move="left" aria-label="Move left">←</button><button data-move="back" aria-label="Move backward">↓</button><button data-move="right" aria-label="Move right">→</button></div></div>
      <div class="scene-bottom"><div class="navigation-help" id="navigation-help"><span class="mouse-mark">↔</span><span>Drag to orbit <b>·</b> Scroll to zoom <b>·</b> Right-drag to pan</span></div><span class="scale-note">MODEL IN METERS</span></div>
      <div id="error" role="alert" hidden></div>
    </section>
  </main>
  <footer class="facts"><div><strong>03</strong><span>Bedrooms</span></div><div><strong>02</strong><span>Full bathrooms</span></div><div><strong>${areas.combined_floor.toFixed(1)}<small> m²</small></strong><span class="area-imperial">${squareFeet(areas.combined_floor)} ft²</span><span>Combined floor area</span></div><div><strong>${areas.covered_terrace}<small> m²</small></strong><span class="area-imperial">${squareFeet(areas.covered_terrace)} ft²</span><span>Covered terrace</span></div><p>Room to gather.<br><em>Space to slow down.</em></p></footer>`;

const $ = <T extends HTMLElement>(id: string) =>
  document.getElementById(id) as T;
const sceneElement = $("scene");
const scene = new THREE.Scene();
scene.background = new THREE.Color("#e9e5dc");
scene.fog = new THREE.Fog("#e9e5dc", 45, 100);
const camera = new THREE.PerspectiveCamera(45, 1, 0.05, 140);
let renderer: THREE.WebGLRenderer;
try {
  renderer = new THREE.WebGLRenderer({
    antialias: true,
    powerPreference: "high-performance",
  });
} catch {
  $("error").hidden = false;
  $("error").textContent =
    "This browser could not start 3D graphics. Enable hardware acceleration or try a WebGL-capable browser.";
  throw new Error("WebGL unavailable");
}
const gl = renderer.getContext();
const rendererInfo = gl.getExtension("WEBGL_debug_renderer_info");
const softwareRenderer = rendererInfo
  ? /swiftshader|llvmpipe|softpipe|software/i.test(
      String(gl.getParameter(rendererInfo.UNMASKED_RENDERER_WEBGL)),
    )
  : false;
sceneElement.dataset.renderTier = softwareRenderer ? "software" : "hardware";
renderer.setPixelRatio(
  softwareRenderer ? 1 : Math.min(window.devicePixelRatio, 2),
);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
renderer.info.autoReset = false;
sceneElement.appendChild(renderer.domElement);
const ambient = new THREE.HemisphereLight("#f5f5ff", "#b4c0c9", 1.75);
scene.add(ambient);
const sun = new THREE.DirectionalLight("#fff2df", 2.6);
sun.position.set(-12, 22, 10);
sun.castShadow = true;
sun.shadow.mapSize.setScalar(softwareRenderer ? 512 : 2048);
sun.shadow.camera.left = -24;
sun.shadow.camera.right = 24;
sun.shadow.camera.top = 24;
sun.shadow.camera.bottom = -24;
sun.shadow.camera.far = 70;
sun.shadow.normalBias = 0.025;
sun.shadow.bias = -0.00008;
scene.add(sun);
const groundPlane = new THREE.Mesh(
  new THREE.PlaneGeometry(200, 200),
  new THREE.MeshStandardMaterial({ color: "#e9e5dc", roughness: 1 }),
);
groundPlane.rotation.x = -Math.PI / 2;
groundPlane.position.y = -0.27;
groundPlane.receiveShadow = true;
scene.add(groundPlane);
const model = createHouse(scene);
const environmentScene = new RoomEnvironment();
const pmrem = new THREE.PMREMGenerator(renderer);
const environment = pmrem.fromScene(environmentScene, 0.04);
environmentScene.dispose();
pmrem.dispose();
scene.environment = environment.texture;
sceneElement.dataset.textures = "loading";
let active = true;
void loadMaterialTextures(
  softwareRenderer ? 1 : renderer.capabilities.getMaxAnisotropy(),
).then((complete) => {
  if (!active) return;
  sceneElement.dataset.textures = complete ? "ready" : "partial";
  $("material-status").hidden = complete;
  if (!complete)
    $("material-status").textContent =
      "Some finishes could not load; simple surfaces are shown.";
});
const depthRenderer = createDepthRenderer(renderer, scene, camera);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.maxPolarAngle = Math.PI / 2 - 0.02;
controls.minDistance = 3;
controls.maxDistance = 50;
let view: View = "exterior",
  walking = false,
  feet = 0,
  yaw = 0,
  pitch = 0;
let lastMapFloor: Floor | undefined;
const keys = new Set<string>();
const eyeHeight = 1.65;
const floorOfCamera = (): Floor => (feet > 2.5 ? "upper" : "ground");
const activeFloor = (): Floor =>
  walking ? floorOfCamera() : view === "upper" ? "upper" : "ground";

function updateModel() {
  const realistic = $<HTMLInputElement>("materials").checked;
  setRealisticMaterials(realistic);
  scene.environmentIntensity = realistic ? 0.55 : 0;
  ambient.intensity = realistic ? 1.35 : 1.75;
  sceneElement.dataset.materials = realistic ? "realistic" : "simple";
  model.setDepthCues($<HTMLInputElement>("depth").checked);
  model.setGateOpen($<HTMLInputElement>("gate").checked);
  const drainageVisible =
    $<HTMLInputElement>("drainage").checked &&
    view === "exterior" &&
    !walking &&
    $<HTMLInputElement>("roof").checked;
  model.setDrainageVisible(drainageVisible);
  $("drainage-legend").hidden = !drainageVisible;
  sceneElement.dataset.gate = $<HTMLInputElement>("gate").checked
    ? "open"
    : "closed";
  sceneElement.dataset.drainage = String(drainageVisible);
  model.setView(
    view,
    walking,
    $<HTMLInputElement>("roof").checked,
    $<HTMLInputElement>("furniture").checked,
  );
  $<HTMLInputElement>("roof").disabled = walking || view !== "exterior";
  $<HTMLInputElement>("drainage").disabled =
    walking || view !== "exterior" || !$<HTMLInputElement>("roof").checked;
  $("rear").hidden = walking || view !== "exterior";
}
function paintMap() {
  const floor = activeFloor();
  lastMapFloor = floor;
  const floorRooms = rooms.filter((r) => r.floor === floor);
  $("map-title").textContent =
    floor === "ground" ? "Ground floor" : "Upper floor";
  const svg = document.getElementById("minimap")!;
  const d = floor === "ground" ? 10.5 : 9.5;
  // Reverse plan depth so the street stays at the bottom, as in the source plans.
  svg.innerHTML = `<rect x="0" y="${10.5 - d}" width="9" height="${d}" fill="#dfd4bf"/>${floorRooms
    .map((r) => {
      const [x, depth, w, h] = r.rect;
      return `<g class="map-room" role="button" tabindex="0" data-room="${r.id}" aria-label="Enter ${r.name}"><rect x="${x}" y="${10.5 - depth - h}" width="${w}" height="${h}" fill="${/bathroom/.test(r.name) ? "#bfcac1" : /bedroom/.test(r.name) ? "#d8c1a1" : "#e8ddc9"}"/><text x="${x + w / 2}" y="${10.5 - depth - h / 2 + 0.13}" text-anchor="middle">${r.id}</text></g>`;
    })
    .join("")}${wallSolids(floor)
    .filter((w) => w.bottom < levels[floor] + 0.1)
    .map((w) => {
      const { x, z: depth, w: width, d: h } = w;
      return `<rect x="${x}" y="${10.5 - depth - h}" width="${width}" height="${h}" fill="#777c68" pointer-events="none"/>`;
    })
    .join(
      "",
    )}<g id="map-camera" pointer-events="none"><circle r=".24" fill="#a65339" stroke="#fff9eb" stroke-width=".1"/><path d="M-.22,-.32 L0,-.65 .22,-.32" fill="#a65339"/></g>`;
  svg.querySelectorAll<SVGGElement>("[data-room]").forEach((el) => {
    el.addEventListener("click", () => enterRoom(el.dataset.room!));
    el.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        enterRoom(el.dataset.room!);
      }
    });
  });
}
function updateMapCamera() {
  if (lastMapFloor !== activeFloor()) paintMap();
  const marker = document.getElementById("map-camera")!;
  marker.setAttribute(
    "visibility",
    walking &&
      camera.position.x >= 0 &&
      camera.position.x <= 9 &&
      -camera.position.z >= 0 &&
      -camera.position.z <= 10.5
      ? "visible"
      : "hidden",
  );
  marker.setAttribute(
    "transform",
    `translate(${camera.position.x} ${10.5 + camera.position.z}) rotate(${(-yaw * 180) / Math.PI})`,
  );
}
function setView(next: View) {
  view = next;
  setWalking(false);
  keys.clear();
  const targetY = next === "upper" ? levels.upper : 0;
  if (next === "exterior") {
    camera.position.set(-17, 14, 22);
    controls.target.set(4, 2.2, -4);
  } else {
    camera.position.set(-7, targetY + 16, 12);
    controls.target.set(4.5, targetY, -5);
  }
  camera.position
    .sub(controls.target)
    .multiplyScalar(Math.max(1, 0.95 / camera.aspect))
    .add(controls.target);
  camera.fov = 45;
  camera.updateProjectionMatrix();
  controls.update();
  document
    .querySelectorAll<HTMLButtonElement>("[data-view]")
    .forEach((el) =>
      el.setAttribute("aria-pressed", String(el.dataset.view === next)),
    );
  $("view-label").textContent =
    next === "exterior"
      ? "01 / EXTERIOR"
      : next === "ground"
        ? "02 / GROUND FLOOR"
        : "03 / UPPER FLOOR";
  $("scene-heading").textContent =
    next === "exterior"
      ? "The whole picture."
      : next === "ground"
        ? "Made for gathering."
        : "A quieter kind of space.";
  $("view-status").textContent =
    `${next === "exterior" ? "Exterior" : next === "ground" ? "Ground floor" : "Upper floor"} · orbit view`;
  $<HTMLSelectElement>("room").value = "";
  paintMap();
  updateModel();
}
function setWalking(value: boolean) {
  walking = value;
  controls.enabled = !value;
  $("orbit").setAttribute("aria-pressed", String(!value));
  $("walk").setAttribute("aria-pressed", String(value));
  $("crosshair").hidden = !value;
  $("touch-controls").hidden = !value;
  document.body.classList.toggle("walking", value);
  $("navigation-help").innerHTML = value
    ? '<span class="mouse-mark">↑</span><span>WASD / arrows to move <b>·</b> Drag to look <b>·</b> Esc to orbit</span>'
    : '<span class="mouse-mark">↔</span><span>Drag to orbit <b>·</b> Scroll to zoom <b>·</b> Right-drag to pan</span>';
  if (!value && document.pointerLockElement) document.exitPointerLock();
  updateModel();
}
function startWalk(
  x = 4.8,
  depth = view === "exterior" ? -1.4 : 1,
  floor: Floor = view === "upper" ? "upper" : "ground",
) {
  feet = levels[floor];
  yaw = 0;
  pitch = 0;
  camera.position.set(x, feet + eyeHeight, -depth);
  camera.fov = 68;
  camera.updateProjectionMatrix();
  camera.rotation.order = "YXZ";
  camera.rotation.set(pitch, yaw, 0);
  setWalking(true);
  paintMap();
  sceneElement.focus({ preventScroll: true });
  $("view-status").textContent =
    `${floor === "ground" ? "Ground floor" : "Upper floor"} · eye level ${eyeHeight.toFixed(2)} m`;
}
function enterRoom(id: string) {
  const room = rooms.find((r) => r.id === id);
  if (!room) return;
  const position = roomViewpoints[id];
  if (!position) return;
  view = room.floor;
  document
    .querySelectorAll<HTMLButtonElement>("[data-view]")
    .forEach((el) =>
      el.setAttribute("aria-pressed", String(el.dataset.view === room.floor)),
    );
  startWalk(position[0], position[1], room.floor);
  yaw = position[2];
  pitch = ["G2", "U2", "G3", "G8"].includes(id) ? -0.38 : -0.16;
  $("scene-heading").textContent = room.name;
  $("view-label").textContent =
    `${room.id}${["G4", "G5"].includes(room.id) ? " reference zone" : ""} / ${room.area.toFixed(1)} m² · ${squareFeet(room.area)} ft²`;
  $<HTMLSelectElement>("room").value = id;
}

document
  .querySelectorAll<HTMLButtonElement>("[data-view]")
  .forEach((el) =>
    el.addEventListener("click", () => setView(el.dataset.view as View)),
  );
$("walk").addEventListener("click", () => {
  if (!walking) startWalk();
});
$("orbit").addEventListener("click", () =>
  setView(walking ? activeFloor() : view),
);
$("rear").addEventListener("click", () => {
  setView("exterior");
  camera.position.set(20, 12, -29);
  controls.target.set(4.5, 2.8, -6);
  controls.update();
});
$("reset").addEventListener("click", () => setView(view));
$("fullscreen").addEventListener("click", async () => {
  try {
    if (document.fullscreenElement) await document.exitFullscreen();
    else await document.documentElement.requestFullscreen();
  } catch {
    $("view-status").textContent = "Fullscreen is unavailable in this browser.";
  }
});
for (const id of [
  "roof",
  "furniture",
  "depth",
  "gate",
  "drainage",
  "materials",
])
  $(id).addEventListener("change", updateModel);
$("room").addEventListener("change", (e) =>
  enterRoom((e.target as HTMLSelectElement).value),
);
window.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && walking) {
    setView(activeFloor());
    return;
  }
  if (
    !walking ||
    (e.target instanceof HTMLElement &&
      ["INPUT", "SELECT", "BUTTON", "SUMMARY"].includes(e.target.tagName))
  )
    return;
  const key = e.key.toLowerCase();
  if (
    [
      "w",
      "a",
      "s",
      "d",
      "arrowup",
      "arrowleft",
      "arrowdown",
      "arrowright",
      "shift",
    ].includes(key)
  ) {
    keys.add(key);
    e.preventDefault();
  }
});
window.addEventListener("keyup", (e) => keys.delete(e.key.toLowerCase()));
window.addEventListener("blur", () => keys.clear());
document.addEventListener("visibilitychange", () => {
  if (document.hidden) keys.clear();
});
let drag: { id: number; x: number; y: number } | null = null;
renderer.domElement.addEventListener("pointerdown", (e) => {
  if (!walking) return;
  sceneElement.focus({ preventScroll: true });
  drag = { id: e.pointerId, x: e.clientX, y: e.clientY };
  renderer.domElement.setPointerCapture(e.pointerId);
});
renderer.domElement.addEventListener("pointermove", (e) => {
  if (!walking || !drag || drag.id !== e.pointerId) return;
  yaw -= (e.clientX - drag.x) * 0.004;
  pitch -= (e.clientY - drag.y) * 0.004;
  pitch = THREE.MathUtils.clamp(pitch, -1.35, 1.35);
  drag.x = e.clientX;
  drag.y = e.clientY;
});
for (const event of ["pointerup", "pointercancel", "lostpointercapture"])
  renderer.domElement.addEventListener(event, () => {
    drag = null;
  });
const touchKeys: Record<string, string> = {
  forward: "w",
  back: "s",
  left: "a",
  right: "d",
};
document
  .querySelectorAll<HTMLButtonElement>("[data-move]")
  .forEach((button) => {
    const key = touchKeys[button.dataset.move!];
    button.addEventListener("pointerdown", (e) => {
      e.preventDefault();
      button.setPointerCapture(e.pointerId);
      keys.add(key);
    });
    for (const event of ["pointerup", "pointercancel", "lostpointercapture"])
      button.addEventListener(event, () => keys.delete(key));
  });
const observer = new ResizeObserver(() => {
  const width = sceneElement.clientWidth,
    height = sceneElement.clientHeight;
  if (width && height) {
    const aspect = width / height;
    if (!walking)
      camera.position
        .sub(controls.target)
        .multiplyScalar(
          Math.max(1, 0.95 / aspect) / Math.max(1, 0.95 / camera.aspect),
        )
        .add(controls.target);
    // Keep controls at full CSS resolution while software GPUs draw fewer pixels.
    const scale = softwareRenderer
      ? Math.min(1, Math.sqrt(240_000 / (width * height)))
      : 1;
    renderer.setPixelRatio(
      softwareRenderer ? scale : Math.min(window.devicePixelRatio, 2),
    );
    renderer.setSize(width, height);
    depthRenderer.resize(Math.round(width * scale), Math.round(height * scale));
    camera.aspect = aspect;
    camera.updateProjectionMatrix();
  }
});
observer.observe(sceneElement);
renderer.domElement.addEventListener("webglcontextlost", (e) => {
  e.preventDefault();
  $("error").hidden = false;
  $("error").textContent =
    "3D graphics paused. Reload the page to restore the model.";
});
setView("exterior");
let previous = performance.now();
function frame(now: number) {
  const dt = Math.min((now - previous) / 1000, 0.05);
  previous = now;
  if (walking) {
    camera.rotation.set(pitch, yaw, 0);
    let forward =
      Number(keys.has("w") || keys.has("arrowup")) -
      Number(keys.has("s") || keys.has("arrowdown"));
    let right =
      Number(keys.has("d") || keys.has("arrowright")) -
      Number(keys.has("a") || keys.has("arrowleft"));
    const length = Math.hypot(forward, right);
    if (length) {
      forward /= length;
      right /= length;
      const speed = (keys.has("shift") ? 3 : 1.6) * dt;
      const dx = (-Math.sin(yaw) * forward + Math.cos(yaw) * right) * speed;
      const dz = (-Math.cos(yaw) * forward - Math.sin(yaw) * right) * speed;
      // Resolve axes separately to slide along walls without tunneling.
      const xFloor = tryMove(camera.position.x + dx, -camera.position.z, feet);
      if (xFloor !== null) {
        camera.position.x += dx;
        feet = xFloor;
      }
      const zFloor = tryMove(camera.position.x, -camera.position.z - dz, feet);
      if (zFloor !== null) {
        camera.position.z += dz;
        feet = zFloor;
      }
      camera.position.y = THREE.MathUtils.damp(
        camera.position.y,
        feet + eyeHeight,
        18,
        dt,
      );
      $("view-status").textContent =
        `${feet > 0.2 && feet < 3.2 ? "Stair" : floorOfCamera() === "upper" ? "Upper floor" : "Ground floor"} · eye level ${eyeHeight.toFixed(2)} m`;
    }
  } else controls.update();
  updateMapCamera();
  renderer.info.reset();
  const depthEnabled = walking && $<HTMLInputElement>("depth").checked;
  depthRenderer.render(depthEnabled);
  sceneElement.dataset.depth = String(depthEnabled);
  // Read-only diagnostics for browser verification and support.
  sceneElement.dataset.ready = "true";
  sceneElement.dataset.mode = walking ? "walk" : "orbit";
  sceneElement.dataset.position = [camera.position.x, feet, -camera.position.z]
    .map((n) => n.toFixed(3))
    .join(",");
  sceneElement.dataset.drawCalls = String(renderer.info.render.calls);
}
renderer.setAnimationLoop(frame);
// Do not leave stale input or animation listeners after a dev hot update.
if (import.meta.hot)
  import.meta.hot.dispose(() => {
    active = false;
    renderer.setAnimationLoop(null);
    observer.disconnect();
    controls.dispose();
    depthRenderer.dispose();
    environment.dispose();
    disposeMaterialTextures();
    renderer.dispose();
  });
