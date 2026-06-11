# Lab 13 – Three.js cz. 1 – Eksport z Blendera, Scena i GLTFLoader

## Co zostało zrealizowane

Wyeksportowano scenę biomechaniczną ze `swiatozywiony12.blend` (roślina + pająk + wybrane cząsteczki) do pliku `biomech13.glb`.

Zbudowano aplikację webową bez bundlera z:
- `WebGLRenderer` + `PerspectiveCamera` + `OrbitControls` (damping, min/maxDistance)
- oświetleniem Three-Point
- asynchronicznym wczytaniem modelu przez `GLTFLoader` z obsługą błędów
- własną animacją w pętli `requestAnimationFrame` (powolny obrót sceny skalowany przez `THREE.Clock` delta)
- automatycznym centrowaniem kamery na podstawie `THREE.Box3`
- obsługą resize okna
