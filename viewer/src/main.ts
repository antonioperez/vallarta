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
  <header class="masthead"><a class="brand" href="./" aria-label="Las Juntas home"><span class="brand-symbol">lj<span>·</span></span><span>LAS JUNTAS<small>A house in the making</small></span></a><div class="edition"><span class="status-dot"></span> CONCEPT 05 <span class="edition-date">/ SEPTEMBER 2026</span></div></header>
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
      <div class="options"><label><input type="checkbox" id="furniture" checked><span>Furniture</span></label><label><input type="checkbox" id="roof" checked><span>Exterior roof</span></label></div>
      <details class="notes"><summary>About this model <span>+</span></summary><p>Based on Concept 05. Ground ceiling 3.00 m; upper ceiling 2.80 m; floor-to-floor 3.40 m. Window and door heights, roof thickness, materials and landscape details are illustrative. Furniture is simplified; movement collides with walls, not furniture.</p><p>Schematic study. Stair headroom, structure and construction details remain unverified.</p></details>
      <div class="sidebar-footer">10 × 20 m lot <span>·</span> Las Juntas, México</div>
    </aside>
    <section class="viewport" aria-label="Interactive 3D house">
      <div id="scene" tabindex="0" aria-label="3D model. In walk mode use W A S D or arrow keys to move, drag to look, Escape to return to orbit."></div>
      <div class="scene-top"><div class="scene-title"><span class="eyebrow" id="view-label">01 / EXTERIOR</span><h2 id="scene-heading">The whole picture.</h2></div><div class="utilities"><button id="reset" class="icon-button" aria-label="Reset camera" title="Reset camera">${icon.reset}</button><button id="fullscreen" class="icon-button" aria-label="Toggle fullscreen" title="Fullscreen">${icon.expand}</button></div></div>
      <div class="mode-switch" aria-label="Navigation mode"><button id="orbit" aria-pressed="true">${icon.orbit} Orbit</button><button id="walk" aria-pressed="false">${icon.walk} Walk inside</button></div>
      <div id="crosshair" hidden>+</div>
      <div class="view-badge"><span class="status-dot"></span><span id="view-status" role="status" aria-live="polite">Exterior · orbit view</span></div>
      <div class="touch-controls" id="touch-controls" hidden aria-label="Walk controls"><button data-move="forward" aria-label="Move forward">↑</button><div><button data-move="left" aria-label="Move left">←</button><button data-move="back" aria-label="Move backward">↓</button><button data-move="right" aria-label="Move right">→</button></div></div>
      <div class="scene-bottom"><div class="navigation-help" id="navigation-help"><span class="mouse-mark">↔</span><span>Drag to orbit <b>·</b> Scroll to zoom <b>·</b> Right-drag to pan</span></div><span class="scale-note">MODEL IN METERS</span></div>
      <div id="error" role="alert" hidden></div>
    </section>
  </main>
  <footer class="facts"><div><strong>03</strong><span>Bedrooms</span></div><div><strong>02</strong><span>Full bathrooms</span></div><div><strong>${areas.combined_floor.toFixed(1)}<small> m²</small></strong><span>Combined floor area</span></div><div><strong>18<small> m²</small></strong><span>Covered terrace</span></div><p>Room to gather.<br><em>Space to slow down.</em></p></footer>`;

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
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.25;
sceneElement.appendChild(renderer.domElement);
const ambient = new THREE.HemisphereLight("#fff8e9", "#a3a68b", 2.7);
scene.add(ambient);
const sun = new THREE.DirectionalLight("#fff4da", 3.4);
sun.position.set(-12, 22, 10);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
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
  model.setView(
    view,
    walking,
    $<HTMLInputElement>("roof").checked,
    $<HTMLInputElement>("furniture").checked,
  );
  $<HTMLInputElement>("roof").disabled = walking || view !== "exterior";
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
    controls.target.set(4, 1.5, -4);
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
  $("scene-heading").textContent = room.name;
  $("view-label").textContent = `${room.id} / ${room.area.toFixed(1)} m²`;
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
$("reset").addEventListener("click", () => setView(view));
$("fullscreen").addEventListener("click", async () => {
  try {
    if (document.fullscreenElement) await document.exitFullscreen();
    else await document.documentElement.requestFullscreen();
  } catch {
    $("view-status").textContent = "Fullscreen is unavailable in this browser.";
  }
});
for (const id of ["roof", "furniture"])
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
    renderer.setSize(width, height);
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
  renderer.render(scene, camera);
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
    renderer.setAnimationLoop(null);
    observer.disconnect();
    controls.dispose();
    renderer.dispose();
  });
