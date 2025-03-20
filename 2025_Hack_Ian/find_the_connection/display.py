import numpy as np
import trimesh
"""
Libraries and functions for mesh displaying 
"""
# ====================================================================
# Display Functions
# ==============================================================  ======
def clipping_plane():
   return
def display_mesh(vf_list):
  meshes = [trimesh.Trimesh(vertices =v, faces =f) for v,f in vf_list]
  scene = trimesh.Scene(meshes)
  scene.show()
def colour_palette():
   return
def display_points(points, radius=0.05):
    # Create a sphere mesh at each point
    spheres = []
    for point in points:
        s = trimesh.creation.icosphere(subdivisions=3, radius=radius)  # High-quality sphere
        s.apply_translation(point)
        s.visual.face_colors = [0, 255, 255, 255]
        spheres.append(s)
    return spheres
def display_vector(vectors):
   """
   Example Input:
   p1 = np.array([0, 0, 0])
   p2 = np.array([1, 2, 3])
   vectors[i] =  np.vstack((p1, p2))
   """
   edges = np.array([[0, 1]]) 
   paths = []
   for vector in vectors:
    path = trimesh.load_path(vertices=vector, edges=edges)
    path.visual.vertex_colors = [0, 0, 255, 255]
    path.visual.face_colors = [0, 0, 255, 150]
    paths.append(path)
   return paths

