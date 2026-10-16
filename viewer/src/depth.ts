import * as THREE from "three";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { SSAOPass } from "three/addons/postprocessing/SSAOPass.js";
import { OutputPass } from "three/addons/postprocessing/OutputPass.js";

export function createDepthRenderer(
  renderer: THREE.WebGLRenderer,
  scene: THREE.Scene,
  camera: THREE.PerspectiveCamera,
) {
  const target = new THREE.WebGLRenderTarget(1, 1, {
    type: THREE.HalfFloatType,
    samples: 4,
  });
  const composer = new EffectComposer(renderer, target);
  // Limit postprocessing to CSS pixel resolution, including high-DPI phones.
  composer.setPixelRatio(1);
  const beauty = new RenderPass(scene, camera);
  const ao = new SSAOPass(scene, camera, 1, 1, 16);
  ao.kernelRadius = 0.24;
  ao.minDistance = 0.00015;
  ao.maxDistance = 0.012;
  const output = new OutputPass();
  composer.addPass(beauty);
  composer.addPass(ao);
  composer.addPass(output);
  return {
    resize(width: number, height: number) {
      composer.setSize(width, height);
    },
    render(enabled: boolean) {
      if (enabled) {
        // SSAOPass only synchronizes projection in setSize; orbit/walk changes FOV
        // without resizing. Keep reconstruction aligned with the actual camera.
        ao.ssaoMaterial.uniforms.cameraProjectionMatrix.value.copy(
          camera.projectionMatrix,
        );
        ao.ssaoMaterial.uniforms.cameraInverseProjectionMatrix.value.copy(
          camera.projectionMatrixInverse,
        );
        composer.render();
      } else renderer.render(scene, camera);
    },
    dispose() {
      ao.dispose();
      beauty.dispose();
      output.dispose();
      composer.dispose();
    },
  };
}
