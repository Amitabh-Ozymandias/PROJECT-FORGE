import { useEffect, useMemo, useState } from "react";
import { api } from "./api";
import brandMark from "./assets/hephaestus-hammer-anvil.png";
import type { Design, Geometry, Project, SimulationRun } from "./types";
import { Viewport } from "./Viewport";

const millimetres = (metres: number) => (metres * 1000).toFixed(1);

export function App() {
  const [project, setProject] = useState<Project | null>(null);
  const [geometry, setGeometry] = useState<Geometry | null>(null);
  const [run, setRun] = useState<SimulationRun | null>(null);
  const [status, setStatus] = useState("Connecting to local engineering service…");
  const [busy, setBusy] = useState(false);

  const refreshGeometry = async (id: string) => setGeometry(await api.geometry(id));
  useEffect(() => { void (async () => {
    try {
      const projects = await api.listProjects();
      const active = projects[0] ? await api.getProject(projects[0].project_id) : await api.createProject("Cantilever Bracket");
      setProject(active); await refreshGeometry(active.project_id); setStatus("Local workspace ready");
    } catch (error) { setStatus(error instanceof Error ? error.message : "Unable to start workspace"); }
  })(); }, []);

  const dimensions = useMemo(() => project?.design.part, [project]);
  const changeDimension = (key: keyof Design["part"], value: string) => {
    if (!project || !Number.isFinite(Number(value)) || Number(value) <= 0) return;
    setProject({ ...project, design: { ...project.design, part: { ...project.design.part, [key]: Number(value) / 1000 } } });
  };
  const saveGeometry = async () => {
    if (!project) return;
    setBusy(true); setStatus("Saving parametric design…");
    try { const saved = await api.saveDesign(project.project_id, project.design); setProject(saved); await refreshGeometry(saved.project_id); setStatus("Geometry saved locally"); }
    catch (error) { setStatus(error instanceof Error ? error.message : "Save failed"); }
    finally { setBusy(false); }
  };
  const analyse = async () => {
    if (!project) return;
    setBusy(true); setStatus("Running deterministic static analysis…");
    try { const response = await api.runStatic(project.project_id); setRun(response.run); setStatus("Analysis complete — result saved with this project"); }
    catch (error) { setStatus(error instanceof Error ? error.message : "Analysis failed"); }
    finally { setBusy(false); }
  };

  return <main className="app-shell">
    <header><div className="brand"><img src={brandMark} alt="HEPHAESTUS hammer and anvil" /><div><span className="eyebrow">DIGITAL ENGINEERING LABORATORY</span><h1>HEPHAESTUS</h1></div></div><p className="status"><i />{status}</p></header>
    <section className="workspace">
      <aside className="panel left-panel">
        <h2>{project?.name ?? "Loading project"}</h2><p className="muted">Parametric cantilever · SI engineering model</p>
        <h3>Geometry</h3>
        {dimensions && <div className="fields">
          <label>Length <input aria-label="Length in millimetres" type="number" step="1" value={millimetres(dimensions.length_m)} onChange={(e) => changeDimension("length_m", e.target.value)} /><small>mm</small></label>
          <label>Width <input aria-label="Width in millimetres" type="number" step="1" value={millimetres(dimensions.width_m)} onChange={(e) => changeDimension("width_m", e.target.value)} /><small>mm</small></label>
          <label>Height <input aria-label="Height in millimetres" type="number" step="1" value={millimetres(dimensions.height_m)} onChange={(e) => changeDimension("height_m", e.target.value)} /><small>mm</small></label>
        </div>}
        <button onClick={saveGeometry} disabled={!project || busy}>Update geometry</button>
        <h3>Load case</h3><p>{project?.design.load_case.name}<strong>{project?.design.load_case.end_force_n} N</strong></p>
        <h3>Material</h3><p>{project?.design.material.name}</p>
      </aside>
      <section className="view-panel"><Viewport geometry={geometry} /><div className="view-toolbar"><span>{geometry?.generator ?? "—"}</span><span>{geometry ? `${millimetres(geometry.dimensions_m.length)} × ${millimetres(geometry.dimensions_m.width)} × ${millimetres(geometry.dimensions_m.height)} mm` : ""}</span></div></section>
      <aside className="panel right-panel">
        <h2>Engineering run</h2><p className="muted">Static cantilever analysis</p><button className="primary" onClick={analyse} disabled={!project || busy}>Run analysis</button>
        {run ? <div className={`result ${run.result.passes ? "pass" : "fail"}`}><h3>{run.result.passes ? "Constraint pass" : "Constraint fail"}</h3><p>Stress <strong>{(run.result.maximum_bending_stress_pa / 1e6).toFixed(1)} MPa</strong></p><p>Deflection <strong>{millimetres(run.result.tip_deflection_m)} mm</strong></p><p>Safety factor <strong>{run.result.factor_of_safety.toFixed(2)}</strong></p><p>Mass <strong>{(run.result.mass_kg * 1000).toFixed(0)} g</strong></p></div> : <p className="empty">Run an analysis to create a traceable local result.</p>}
      </aside>
    </section>
  </main>;
}
