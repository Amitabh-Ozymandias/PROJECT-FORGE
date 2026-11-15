import { useEffect, useRef } from "react";
import * as THREE from "three";
import type { Geometry } from "./types";

export function Viewport({ geometry }: { geometry: Geometry | null }) {
  const container = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const host = container.current;
    if (!host) return;
    const scene = new THREE.Scene();
    scene.background = new THREE.Color("#10141b");
    const camera = new THREE.PerspectiveCamera(45, host.clientWidth / host.clientHeight, 0.001, 100);
    camera.position.set(0.18, -0.22, 0.16);
    camera.lookAt(0, 0, 0);
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(host.clientWidth, host.clientHeight);
    host.appendChild(renderer.domElement);
    scene.add(new THREE.HemisphereLight(0xbad9ff, 0x152030, 2.5));
    const light = new THREE.DirectionalLight(0xffffff, 2.5); light.position.set(0.1, -0.2, 0.3); scene.add(light);
    scene.add(new THREE.GridHelper(0.5, 10, 0x405269, 0x273441));
    let mesh: THREE.Mesh | null = null;
    if (geometry) {
      const buffer = new THREE.BufferGeometry();
      buffer.setAttribute("position", new THREE.Float32BufferAttribute(geometry.vertices.flat(), 3));
      buffer.setIndex(geometry.triangles);
      buffer.computeVertexNormals();
      mesh = new THREE.Mesh(buffer, new THREE.MeshStandardMaterial({ color: 0x4ca8ff, metalness: 0.35, roughness: 0.34 }));
      scene.add(mesh);
    }
    const render = () => renderer.render(scene, camera);
    render();
    const resize = () => { camera.aspect = host.clientWidth / host.clientHeight; camera.updateProjectionMatrix(); renderer.setSize(host.clientWidth, host.clientHeight); render(); };
    const observer = new ResizeObserver(resize); observer.observe(host);
    return () => { observer.disconnect(); mesh?.geometry.dispose(); renderer.dispose(); renderer.domElement.remove(); };
  }, [geometry]);
  return <div className="viewport" ref={container}>{!geometry && <span className="viewport-empty">Generating local geometry…</span>}</div>;
}
