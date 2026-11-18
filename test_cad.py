import cadquery as cq

# Create a 50mm cube
model = (
    cq.Workplane("XY")
    .box(50, 50, 50)
)

# Export as STEP
cq.exporters.export(model, "test_cube.step")

# Export as STL for Three.js preview
cq.exporters.export(model, "test_cube.stl")

print("CAD model generated successfully!")
print("Volume:", model.val().Volume())