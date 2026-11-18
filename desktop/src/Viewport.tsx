import { useEffect, useRef } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import type { Geometry } from "./types";

export function Viewport({ geometry }: { geometry: Geometry | null }) {
  const container = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const host = container.current;
    if (!host) return;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color("#0e1319");

    const camera = new THREE.PerspectiveCamera(45, host.clientWidth / host.clientHeight, 0.001, 100);
    camera.position.set(0.2, 0.18, 0.25);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(host.clientWidth, host.clientHeight);
    host.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.target.set(0, 0, 0);

    // Studio Lighting
    scene.add(new THREE.AmbientLight(0xdbe6f5, 1.2));

    const keyLight = new THREE.DirectionalLight(0xffffff, 2.2);
    keyLight.position.set(0.3, 0.5, 0.4);
    scene.add(keyLight);

    const fillLight = new THREE.DirectionalLight(0x759ac0, 1.2);
    fillLight.position.set(-0.3, -0.2, -0.3);
    scene.add(fillLight);

    const topLight = new THREE.DirectionalLight(0xa5c9eb, 0.8);
    topLight.position.set(0, 0.8, 0);
    scene.add(topLight);

    // Ground orientation grid
    const grid = new THREE.GridHelper(0.6, 24, 0x3b536b, 0x1d2936);
    grid.position.y = -0.06;
    scene.add(grid);

    let mesh: THREE.Mesh | null = null;
    let edgeLines: THREE.LineSegments | null = null;

    if (geometry && geometry.vertices.length > 0) {
      const buffer = new THREE.BufferGeometry();
      buffer.setAttribute("position", new THREE.Float32BufferAttribute(geometry.vertices.flat(), 3));
      buffer.setIndex(geometry.triangles);
      buffer.computeVertexNormals();
      buffer.computeBoundingBox();

      const material = new THREE.MeshStandardMaterial({
        color: 0x3d8be6,
        metalness: 0.3,
        roughness: 0.35,
      });

      mesh = new THREE.Mesh(buffer, material);

      // Add CAD wireframe silhouette edges
      const edges = new THREE.EdgesGeometry(buffer, 25);
      edgeLines = new THREE.LineSegments(
        edges,
        new THREE.LineBasicMaterial({ color: 0x8ec7ff, linewidth: 1 })
      );
      mesh.add(edgeLines);

      // Center geometry at origin for clean orbit rotation
      if (buffer.boundingBox) {
        const center = new THREE.Vector3();
        buffer.boundingBox.getCenter(center);
        mesh.position.sub(center);
        const size = new THREE.Vector3();
        buffer.boundingBox.getSize(size);
        const maxDim = Math.max(size.x, size.y, size.z);
        grid.position.y = -maxDim * 0.7;
      }

      scene.add(mesh);
    }

    let frameId: number;
    const animate = () => {
      frameId = requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    };
    animate();

    const resize = () => {
      if (!host) return;
      camera.aspect = host.clientWidth / host.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(host.clientWidth, host.clientHeight);
    };

    const observer = new ResizeObserver(resize);
    observer.observe(host);

    return () => {
      cancelAnimationFrame(frameId);
      observer.disconnect();
      controls.dispose();
      mesh?.geometry.dispose();
      if (Array.isArray(mesh?.material)) {
        mesh.material.forEach((m) => m.dispose());
      } else {
        mesh?.material.dispose();
      }
      edgeLines?.geometry.dispose();
      (edgeLines?.material as THREE.Material | undefined)?.dispose();
      renderer.dispose();
      renderer.domElement.remove();
    };
  }, [geometry]);

  return (
    <div className="viewport" ref={container}>
      {!geometry && <span className="viewport-empty">Generating local CadQuery geometry…</span>}
      <div className="viewport-overlay-hint">Rotate: Left-drag · Pan: Right-drag · Zoom: Scroll</div>
    </div>
  );
}
