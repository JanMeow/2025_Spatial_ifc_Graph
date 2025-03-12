import numpy as np
import trimesh
import collision
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
# ====================================================================
# 3D Boolean Operations
# ====================================================================
def boolean_3D(node1, node2, type ="union"):
    geom_info1 = node1.geom_info
    geom_info2 = node2.geom_info

    if collision.intersect(geom_info1["bbox"], geom_info2["bbox"]):
        mesh1 = trimesh.Trimesh(vertices =geom_info1["vertex"], faces =geom_info1["faceVertexIndices"])
        mesh2 = trimesh.Trimesh(vertices =geom_info2["vertex"], faces =geom_info2["faceVertexIndices"])

        if type == "union":
            result = mesh1.union(mesh2)

    return np.array(result.vertices, dtype=np.float32),np.array(result.faces, dtype=np.uint32)
def showMesh(v,f):
   mesh = trimesh.Trimesh(vertices =v, faces =f)
   mesh.show()
# ====================================================================
# 2D Boolean Operations
# ====================================================================