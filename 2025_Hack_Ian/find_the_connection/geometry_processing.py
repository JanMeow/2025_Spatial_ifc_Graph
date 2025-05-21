import numpy as np
import trimesh
import trimesh.smoothing
"""
This module contains the boolean opserations that are used for merging collision shapes
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
def align_to_axis(vertex, axis =2):
  if len(np.unique(vertex[:,axis])) == 2:
    return True
  return False
def get_centre_point(bbox):
  return (bbox[0] + bbox[1]) / 2
def is_xzy_box(vertex):
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
  return vs/ np.linalg.norm(vs, axis = 1)[:, np.newaxis]
def decompose_2D_from_base(base):
  vs = np.array([base[1]- base[0],base[2] - base[1]])
  sort_indices = np.argsort(np.linalg.norm(vs, axis = 1))
  return vs[sort_indices]
def get_unit_vector(v):
  return v/np.linalg.norm(v)
def get_normal(faces):
    v0, v1, v2 = faces[:,0], faces[:,1], faces[:,2]  
    n = np.cross(v1 - v0, v2 - v0)
    return n/np.linalg.norm(n)
def angle_between(v1, v2):
  v1_u = v1/np.linalg.norm(v1)
  v2_u = v2/np.linalg.norm(v2)
  return np.arccos(np.clip(np.dot(v1_u, v2_u.T), -1.0, 1.0))
def project_points_on_face(points, face_normal, face):
   v = points - face[0]
   proj = np.dot(v, face_normal)[:, np.newaxis] * face_normal
   return points - proj
def get_local_coors(T_matrix, vertex):
    inverse = np.linalg.inv(T_matrix.T)
    ones = np.ones(shape = (vertex.shape[0],1))
    result = np.around(np.hstack((vertex, ones)) @ inverse, 2)
    return result[:,0:-1]
def np_intersect_rows(arr0, arr1, return_type = "ndarray"):
  set0 = set(map(tuple, arr0))
  set1 = set(map(tuple, arr1))
  shared = set0.intersection(set1)
  if return_type == "ndarray":
    return np.array(list(shared))
  elif return_type == "list":
    return list(shared)
  elif return_type == "set":
    return shared
  elif return_type == "index":
    tiled_0 = np.tile(arr0, (1,2)).reshape(arr0.shape[0], 2, -1)
    tiled_1 = np.tile(arr1, (1,2)).reshape(arr1.shape[0], 2, -1)
    mask_0 = np.any(np.all(tiled_0 - np.array(list(shared)) == 0, axis = 2), axis = 1)
    mask_1 = np.any(np.all(tiled_0 - np.array(list(shared)) == 0, axis = 2), axis = 1)
    
    return np.argwhere(mask_0 == True).reshape(-1), np.argwhere(mask_1 == True).reshape(-1)
  else:
    raise ValueError("Invalid return type. Use 'ndarray', 'list', or 'set'.")
def np_intersect_rows_atol(arr1,arr2, atol = 0.01):
  diffs = np.linalg.norm(arr1[:, None, :] - arr2[None, :, :], axis=2)
  matches = diffs < atol
  # arr1 row i matches arr2 row j
  i,j = np.where(matches)
  return i,j
def get_polygon_area(arr):
  x = arr[:,0]
  y = arr[:,1]
  return 0.5 * np.abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))
# ====================================================================
# Display Functions
# ==============================================================  ======
def clipping_plane():
   return
def showMesh(vf_list):
  meshes = [trimesh.Trimesh(vertices =v, faces =f) for v,f in vf_list]
  scene = trimesh.Scene(meshes)
  scene.show()
def colour_palette():
   return
# ====================================================================
# 3D Boolean Operations face
# ====================================================================
def boolean_3D(nodes, operation="union", return_type = "trimesh", engine = "manifold", atol = 0.01):
    """
    Perform a boolean operation (union, intersection, difference) on multiple 3D meshes.

    Parameters:
    - nodes (list): List of nodes containing `geom_info` with "vertex" and "face".
    - operation (str): Type of boolean operation ("union", "intersection", "difference").

    Returns:
    - vertices (np.ndarray): Array of resulting mesh vertices (float32).
    - faces (np.ndarray): Array of resulting mesh faces (uint32).
    """
    # Preprocess the nodes to elimate gap due to floating point error
    preprocessing(nodes, atol = atol)

    if len(nodes) < 2:
        raise ValueError("At least two meshes are required for a boolean operation.")

    # Convert node geometries to trimesh objects
    meshes = [
        trimesh.Trimesh(vertices=node.geom_info["vertex"], 
                        faces=node.geom_info["face"]) 
        for node in nodes
    ]

    if operation == "union":
        result = trimesh.boolean.union(meshes, engine = engine)
    elif operation == "intersection":
        result = trimesh.boolean.intersection(meshes, engine = engine)
    elif operation == "difference":
        result = trimesh.boolean.difference(meshes, engine = engine)
    else:
        raise ValueError(f"Invalid operation type: {operation}")
    result = clean_mesh(result)
    if return_type == "trimesh":
        return result
    elif return_type == "vf_list":
      return np.array(result.vertices, dtype=np.float32), np.array(result.faces, dtype=np.uint32)
def preprocessing(nodes, atol = 0.01):
    for i in range(len(nodes[1:])):
      prev = nodes[i-1]
      current = nodes[i]
      m0 = prev.geom_info["vertex"]
      m1 = current.geom_info["vertex"]
      i,j = np_intersect_rows_atol(m0, m1, atol=atol)
      if len(i) > 0:
        #  set the vertex to be the same
        for m0_idx, m1_idx in zip(i, j):
          current.geom_info["vertex"][m1_idx] = prev.geom_info["vertex"][m0_idx]
    return True
def clean_mesh(mesh):
   mesh.remove_duplicate_faces()
   mesh.merge_vertices()
   mesh.merge_vertices()

   mesh.fix_normals()
   return mesh


# ====================================================================
# 2D Boolean Operations
# ====================================================================