export type Design = {
  design_id: string;
  part: { length_m: number; width_m: number; height_m: number };
  material: { name: string; youngs_modulus_pa: number; yield_strength_pa: number; density_kg_m3: number };
  load_case: { name: string; end_force_n: number };
  constraints: Record<string, number>;
};

export type Project = { project_id: string; name: string; created_at: string; updated_at: string; design: Design };
export type Geometry = { generator: string; vertices: number[][]; triangles: number[]; dimensions_m: Record<string, number> };
export type SimulationRun = { result: { maximum_bending_stress_pa: number; tip_deflection_m: number; factor_of_safety: number; mass_kg: number; passes: boolean } };
