import numpy as np
import trimesh
"""
This module contains the boolean operations that are used for merging collision shapes
or touching shapes
# Task 
# Install conda, meshplot,libigl,PolyFem, 

1. Architect inputs IFC good/bad its not production ready anyways
2. Create product classes for the production companies 
3. Corner type menu, 
4. Component Matching Semi Touching the same type on the same floor, knowing floor thickness
5. (Here we are also not asking what if the type is not declared) minimal inner core, edge cases 
like range betweeen 100-150 then persay 300 wall can never be reached


Task for the week:
1. Get all touching wall type in a group
2. Perform boolean operation using the library could be trimesh/ Pymesh

"""
# ====================================================================
# Helpers Functons
# ====================================================================
def is_xyz_extrusion(node):
  vertex = node.geom_info["vertex"]
  if len(np.unique(vertex[:,2])) == 2:
    return True
  return False
def is_xzy_box(node):
  vertex = node.geom_info["vertex"]
  for i in range(3):
    if len(np.unique(vertex[:,i])) != 2:
        return False
  return True
def get_bbox_dim(bbox):
  return bbox[1] - bbox[0]
def get_base_curve(node):
  vertex = node.geom_info["vertex"]
  lowest_z = node.geom_info["bbox"][0][2]
  return vertex[vertex[:,2] == lowest_z]
def decompose_2D(node):
   base = get_base_curve(node)
   vs = np.array([base[1]- base[0],base[2] - base[1]])
   scalars = np.linalg.norm(vs, axis = 1)
   sorted_idx = np.argsort(scalars)
   return vs[sorted_idx], scalars[sorted_idx]
def get_unit_vector(v):
  return v/np.linalg.norm(v)
def angle_between(v1, v2):
  v1_u = get_unit_vector(v1)
  v2_u = get_unit_vector(v2)
  return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))
def project_points_on_face(points, face_normal, face):
   v = points - face[0]
   proj = np.dot(v, face_normal)[:, np.newaxis] * face_normal
   return points - proj
# ====================================================================
# Display Functions
# ====================================================================
def clipping_plane():
   return
def showMesh(vf_list):
  meshes = [trimesh.Trimesh(vertices =v, faces =f) for v,f in vf_list]
  scene = trimesh.Scene(meshes)
  scene.show()
def colour_palette():
   return
# ====================================================================
# 3D Boolean Operations
# ====================================================================
def boolean_3D(nodes, operation="union"):
    """
    Perform a boolean operation (union, intersection, difference) on multiple 3D meshes.

    Parameters:
    - nodes (list): List of nodes containing `geom_info` with "vertex" and "faceVertexIndices".
    - operation (str): Type of boolean operation ("union", "intersection", "difference").

    Returns:
    - vertices (np.ndarray): Array of resulting mesh vertices (float32).
    - faces (np.ndarray): Array of resulting mesh faces (uint32).
    """
    if len(nodes) < 2:
        raise ValueError("At least two meshes are required for a boolean operation.")

    # Convert node geometries to trimesh objects
    meshes = [
        trimesh.Trimesh(vertices=node.geom_info["vertex"], 
                        faces=node.geom_info["faceVertexIndices"]) 
        for node in nodes
    ]

    if operation == "union":
        result = trimesh.boolean.union(meshes)
    elif operation == "intersection":
        result = trimesh.boolean.intersection(meshes)
    elif operation == "difference":
        result = trimesh.boolean.difference(meshes)
    else:
        raise ValueError(f"Invalid operation type: {operation}")

    return np.array(result.vertices, dtype=np.float32), np.array(result.faces, dtype=np.uint32)
# ====================================================================
# 2D Boolean Operations
# ====================================================================