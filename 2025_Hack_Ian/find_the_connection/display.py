import numpy as np
import trimesh
"""
Libraries and functions for mesh displaying 
"""
# ====================================================================
# Display Functions
# ====================================================================
def clipping_plane():
   return
def colour_palette():
   return
def show(funcs):
   """
    Example Input: display([display_mesh(nodes), display_points(points), display_vector(vectors)])
   """
   scene = trimesh.Scene()
   for geom in funcs:
        scene.add_geometry(geom)
   scene.show()
def mesh(objs, obj_type = "node", show_edges = False, edge_only = False):
   meshes = []
   for obj in objs:
      if obj_type == "node":
         mesh = trimesh.Trimesh(vertices =obj.geom_info["vertex"], faces =obj.geom_info["face"])
      elif obj_type == "vf_list":
         mesh = trimesh.Trimesh(vertices =obj[0], faces =obj[1])
      elif obj_type == "trimesh":
         mesh = obj
      # mesh.visual.face_colors = [50, 50, 50, 100]
      line_colour = [128, 128, 128, 150]
      if edge_only:
         show_edges = True
      else:
         meshes.append(mesh)
      if show_edges == True:
         edges = mesh.edges_unique
         edge_vertices = mesh.vertices[edges]
         for edge in edge_vertices:
            path = trimesh.load_path(edge)
            meshes.append(path)
            for entity in path.entities:
               entity.color = line_colour
   return meshes
def points(points, radius=0.05):
    # Create a sphere mesh at each point
    spheres = []
    for point in points:
        s = trimesh.creation.icosphere(subdivisions=3, radius=radius)  # High-quality sphere
        s.apply_translation(point)
        s.visual.face_colors = [0, 255, 255, 255]
        spheres.append(s)
    return spheres
def vector(vectors, origin = np.array([0,0,0]), length = 1):
   vectors *= length
   colour = [255, 0, 0, 150]
   paths = []
   for vector in vectors:
    v = origin + vector
    v = np.vstack((v, origin))
    path = trimesh.load_path(v)
    for entity in path.entities:
        entity.color = colour
    paths.append(path)
   return paths