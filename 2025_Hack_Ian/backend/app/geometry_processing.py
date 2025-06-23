import numpy as np

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
  scalars = np.linalg.norm(vs, axis = 1)
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
def np_intersect_rows(arr1, arr2):
  set0 = set(map(tuple, arr1))
  set1 = set(map(tuple, arr2))
  shared = set0.intersection(set1)
  return np.array(list(shared))
def np_intersect_rows_atol(arr1,arr2, atol = 0.01):
  diffs = np.linalg.norm(arr1[:, None, :] - arr2[None, :, :], axis=2)
  matches = diffs < atol
  # arr1 row i matches arr2 row j
  i,j = np.where(matches)
  return i,j
def get_polygon_area(arr):
  """
   Assumes the polygon is simple and vertices are ordered.
   """
  x = arr[:,0]
  y = arr[:,1]
  return 0.5 * np.abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))
def get_polygon_area_3d(arr):
  """
  Compute the area of a 3D planar polygon using the general vector method.
  Assumes the polygon is simple and vertices are ordered.
  """
  area_vector = np.zeros(3)
  for i in range(len(arr)):
      p1 = arr[i]
      p2 = arr[(i + 1) % len(arr)]
      area_vector += np.cross(p1, p2)
  return 0.5 * np.linalg.norm(area_vector)
def triangle_areas(vertices, faces):
    A = vertices[faces[:, 0]]
    B = vertices[faces[:, 1]]
    C = vertices[faces[:, 2]]
    # Vector edges
    AB = B - A
    AC = C - A
    # Cross product and norm
    cross = np.cross(AB, AC)
    area = 0.5 * np.linalg.norm(cross, axis=1)
    return area
def check_orientation_and_clean_degenerate(vertices, faces, eps=1e-6):
    A = vertices[faces[:, 0]]
    B = vertices[faces[:, 1]]
    C = vertices[faces[:, 2]]

    face_centers = (A + B + C) / 3
    normals = np.cross(B - A, C - A)
    norms = np.linalg.norm(normals, axis=1, keepdims=True)
    valid = norms[:, 0] > eps
    normals = normals[valid] / norms[valid]
    face_centers = face_centers[valid]
    faces = faces[valid]

    centroid = np.mean(vertices, axis=0)
    to_faces = face_centers - centroid
    dot = np.einsum("ij,ij->i", normals, to_faces)
    orientation = np.sign(dot)
    return normals, orientation, valid
def triangle_mesh_volume(vertices, faces):
  A = vertices[faces[:, 0]]
  B = vertices[faces[:, 1]]
  C = vertices[faces[:, 2]]
  # Compute cross product A x B
  cross = np.cross(A, B)
  # Compute dot with C
  volume = np.einsum('ij,ij->i', cross, C) / 6.0
  return np.abs(np.sum(volume)) 
def remove_unreferenced_vertices(vertices, faces):
    unique_indices = np.unique(faces.flatten())
    index_map = {old: i for i, old in enumerate(unique_indices)}
    new_vertices = vertices[unique_indices]
    new_faces = np.vectorize(index_map.get)(faces)
    return new_vertices, new_faces
def get_rel_position(graph, target_pt):
  world_xyz = graph.bbox
  world_extent = world_xyz[1] - world_xyz[0]
  relative_position = (target_pt - world_xyz[0])/world_extent