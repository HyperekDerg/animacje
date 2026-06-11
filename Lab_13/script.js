import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

const canvas = document.getElementById("c");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0a0a0f);

const camera = new THREE.PerspectiveCamera(
  55,
  window.innerWidth / window.innerHeight,
  0.1,
  100,
);
camera.position.set(-0.2, 0.35, 1.7);
camera.lookAt(-0.1, -0.1, 0);

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

const clock = new THREE.Clock();

const ambientLight = new THREE.AmbientLight(0xcef9f2, 0.6);
scene.add(ambientLight);

const keyLight = new THREE.DirectionalLight(0xab92bf, 6.5);
keyLight.position.set(1, 2, 2);
keyLight.castShadow = true;
keyLight.shadow.mapSize.set(2048, 2048);
keyLight.shadow.camera.near = 0.1;
keyLight.shadow.camera.far = 20;
keyLight.shadow.camera.left = -3;
keyLight.shadow.camera.right = 3;
keyLight.shadow.camera.top = 3;
keyLight.shadow.camera.bottom = -3;
keyLight.shadow.bias = -0.001;
scene.add(keyLight);

const fillLight = new THREE.DirectionalLight(0x4488cc, 1.2);
fillLight.position.set(-3, 1, 2);
scene.add(fillLight);

const rimLight = new THREE.DirectionalLight(0x00ffe5, 2.0);
rimLight.position.set(0, 3, -4);
scene.add(rimLight);

const info = document.getElementById("info");
let model = null;

async function loadModel() {
  const loader = new GLTFLoader();
  try {
    const gltf = await loader.loadAsync("biomech_13.glb");
    model = gltf.scene;

    const box = new THREE.Box3().setFromObject(model);
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());
    const maxDim = Math.max(size.x, size.y, size.z);
    const scale = 2.0 / maxDim;
    model.scale.setScalar(scale);
    model.position.sub(center.multiplyScalar(scale));

    scene.add(model);

    let meshCount = 0;
    model.traverse((node) => {
      if (node.isMesh) {
        node.castShadow = true;
        node.receiveShadow = true;
        meshCount++;
      }
    });

    info.textContent = `biomech_13.glb\nmesh-y: ${meshCount}`;
  } catch (err) {
    info.classList.add("error");
    info.textContent = `Błąd ładowania modelu:\n${err.message ?? err}`;
    console.error("[GLTFLoader]", err);
  }
}

loadModel();

function animate() {
  requestAnimationFrame(animate);
  const delta = clock.getDelta();
  const elapsed = clock.getElapsedTime();
  if (model) model.rotation.y += delta * 0.4;
  void elapsed;
  renderer.render(scene, camera);
}

animate();
