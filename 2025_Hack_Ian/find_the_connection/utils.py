import numpy as np
import trimesh
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape
import collision
import math
from traversal import bfs_traverse, loop_detecton
from geometry_processing import decompose_2D_from_base, angle_between, get_base_curve, get_local_coors, np_intersect_rows, np_intersect_rows, decompose_2D
from collections import deque
# ===================================================================================
# Global Variables for units and tolerance
# ===================================================================================
round_to = 8
atol = 1e-3
# ===================================================================================
# ===================================================================================
# ====================================================================
# Geometry Processing
# ====================================================================
def get_bbox(arr):
  max = np.max(arr, axis = 0)
  min = np.min(arr, axis = 0)
  return np.vstack((min,max))
def get_geom_info(entity, get_global = False, round_to = round_to):
  if hasattr(entity, "Representation"):
    if entity.Representation != None:
      result = {
        "T_matrix": None,
        "vertex": None,
        "face": None,
        "bbox": None
      }
      try:
        settings = ifcopenshell.geom.settings()
        shape = ifcopenshell.geom.create_shape(settings, entity)
        result["T_matrix"] = ifcopenshell.util.shape.get_shape_matrix(shape)
        result["vertex"]  = np.around(ifcopenshell.util.shape.get_vertices(shape.geometry), round_to)
        result["face"] = ifcopenshell.util.shape.get_faces(shape.geometry)

        if get_global:
          vertex = result["vertex"]
          T_matrix = result["T_matrix"]
          ones = np.ones(shape = (vertex.shape[0],1))
          stacked = np.hstack((vertex, ones))
          global_coor = stacked@ T_matrix.T
          global_coor = np.around(global_coor[:,0:-1],round_to)
          result["vertex"] = global_coor

        result["bbox"] = get_bbox(result["vertex"])
        return result
      except:
        return None
def get_triangulated_equation(A, B, C):
  # Compute vectors V1 and V2
  V1 = B - A
  V2 = C - A
  # Compute the normal vector (A, B, C) using cross product
  normal = np.cross(V1, V2)
  A, B, C = normal
  # Compute D using the plane equation
  D = -np.dot(normal, A)  # Substituting A into Ax + By + Cz + D = 0
  # Print(equation)
  print(f"Plane equation: {A}x + {B}y + {C}z + {D} = 0")
  return A, B, C, D
def get_triangulated_planes(node):
  if node.geom_info == None:
    print("Node has no geometry")
    return None
  geom_info =  node.geom_info
  vertex = geom_info["vertex"]
  vertex_indices = geom_info["face"]

  arr_shape = (vertex_indices.shape[0], vertex_indices.shape[1], vertex.shape[1])
  array = np.zeros(arr_shape, dtype = np.float32)
  for i,index in enumerate(vertex_indices):
      A, B, C = vertex[index[0]], vertex[index[1]], vertex[index[2]]
      v_stack = np.vstack((A,B,C))
      array[i] = v_stack
  return array
# ====================================================================
# Graph Helper Functions
# ====================================================================
def merge_test(node, node_n, geom_info_for_check, atol = atol):
  """
    Condition of merging for two nodes (wall)
    1. Same Geometry Type
    2. Same Z location to start
    3. Same height a
    4. Same width base curve
    6. Same direction of traversal 
    6. Same Psets #not confirmed the format yet

    roof:
    #need OBB
    1. test upper plane the same
    2. same thickness
  """
  # if they are not of same type, no need check anything, imeediately return False
  geom_type = node.geom_type
  if geom_type != node_n.geom_type:
    return False
  # if Psets are different, return False, except base quantities
  # if "BaseQuantities" in node.psets or "BaseQuantities"  in node_n.psets:
  #   p1 = {k: v for k,v in node.psets.items() if k != "BaseQuantities"}
  #   p2 = {k: v for k,v in node_n.psets.items() if k != "BaseQuantities"}
  #   if p1 != p2:
  #       return False
  # else:
  #   if node.psets != node_n.psets:
  #     return False
  # Check geometric properties to compare
  geom_info_for_check2 = get_geom_info_for_check(node_n)
  if geom_info_for_check2 == False:
    return False
  # Different Geometric check based on type
  if geom_type == "IfcWall":
    bbox1 = geom_info_for_check["AABB"]
    bbox2 = geom_info_for_check2["AABB"]
    height1 = bbox1[1][2] - bbox1[0][2]
    height2 = bbox2[1][2] - bbox2[0][2]
    b1 = geom_info_for_check["base"]
    v1 = geom_info_for_check["vectors"]
    b2 = geom_info_for_check2["base"]
    v2 = geom_info_for_check2["vectors"]
    # Make sure they have intersecting base curve
    base_intersection = np_intersect_rows(b1,b2)
    # the -1 index is the longest vector which defines the traverse direction
    angles = angle_between(v1[1], v2[1])
    conditions =[
      abs(bbox1[0][2] - bbox2[0][2] )< atol, # Same Z location to start
      abs(height1 - height2) < atol, # Same height 
      len(base_intersection) ==2,  # 2 touching vertex in base curve 
      np.abs(angles) < atol or np.abs(angles - math.pi) < atol]
  elif geom_type == "IfcSlab":
    bbox1 = geom_info_for_check["AABB"]
    bbox2 = geom_info_for_check2["AABB"]
    height1 = bbox1[1][2] - bbox1[0][2]
    height2 = bbox2[1][2] - bbox2[0][2]
    conditions = [
      abs(bbox1[0][2] - bbox2[0][2] )< atol,
      abs(height1 - height2) < atol]
  elif geom_type == "IfcRoof":
    OOBB1 = geom_info_for_check["OOBB"]
    OOBB2 = geom_info_for_check2["OOBB"]
    conditions = [
      collision.check_pca_similarity(OOBB1[1], OOBB2[1], atol = 1e-3, method = "Hungarian")
  ]
  
  if all(conditions):
    return True
  return False
def get_geom_info_for_check(node):
  geom_info_for_check= {}
  _type = node.geom_type
  try:
    if _type == "IfcWall":
      geom_info_for_check["base"]= get_base_curve(node)
      geom_info_for_check["vectors"] = decompose_2D_from_base(geom_info_for_check["base"])
      geom_info_for_check["AABB"] = node.geom_info["bbox"]
    elif _type == "IfcSlab":
      geom_info_for_check["AABB"] = node.geom_info["bbox"]
    elif _type == "IfcRoof":
      geom_info_for_check["OOBB"] = collision.create_OOBB(node, "PCA")
  except:
    return False
  return geom_info_for_check
def merge(node):
  memory= {
    "T": set(),
    "F": set()
  }
  geom_info_for_check= get_geom_info_for_check(node)
  # Certain geometry are invalid for merging e.g, no 4 points etc
  if geom_info_for_check:
    stack = [node]
    while stack:
      current = stack.pop()
      memory["T"].add(current.guid)
      for node_n in current.near:
        if node_n.guid not in memory["T"] and node_n.guid not in memory["F"]:
          if merge_test(node, node_n, geom_info_for_check, atol = atol):
            stack.append(node_n)
          else: 
            memory["F"].add(node_n.guid)
    return list(memory["T"])
  return []
def write_to_node(current_node):
  if current_node != None:
    geom_infos = get_geom_info(current_node, get_global = True)
    if geom_infos != None:
      # ignore id cause they are not relevant
      psets = {key: {k: v for k, v in subdict.items() if k != "id"}
    for key, subdict in ifcopenshell.util.element.get_psets(current_node).items()}
      node = Node(current_node.Name, current_node.is_a(), current_node.GlobalId, geom_infos, psets)
      return node
# ====================================================================
# Class Definition for Graph and Node 
# ====================================================================
class Graph:
  def __init__(self,root):
    self.root = root
    self.node_dict = {}
    self.bbox = None
    self.longest_axis = None
    self.bvh = None
  def __len__(self):
        return len(self.node_dict)
  def __getitem__(self, guid):
        return self.node_dict[guid]
  def __setitem__(self, guid, node):
        self.node_dict[guid] = node
  def get_bbox(self):
    arr = np.vstack([node.geom_info["bbox"] for node in self.node_dict.values() 
                     if node.geom_info !=None])
    _max = np.max(arr, axis = 0)
    _min = np.min(arr, axis = 0)
    self.bbox = np.vstack((_min,_max))
    self.longest_axis = np.argmax((self.bbox[1] - self.bbox[0]))
    return 
  def sort_nodes_along_axis(self, axis):
    temp = sorted([node for node in self.node_dict.values()],key = lambda x: x.geom_info["bbox"][0][axis] )
    new_dict = {node.guid:node for node in temp}
    self.node_dict = new_dict
    return self.node_dict
  def build_bvh(self):
    sorted_nodes = list(self.sort_nodes_along_axis(self.longest_axis).values())
    self.bvh = collision.build_bvh(sorted_nodes)
    return 
  def bvh_query(self, bbox):
    collisions = []
    if self.bvh == None:
      print("BVH not built, building now")
      self.build_bvh()
    stack = [self.bvh]
    while stack:
      current_bvh = stack.pop()
      current_bbox = current_bvh.bbox
      if collision.intersect(bbox,current_bbox):
        if current_bvh.leaf:
          collisions.append(current_bvh.nodes)
        if current_bvh.left:
          stack.append(current_bvh.left)
        if current_bvh.right:
          stack.append(current_bvh.right)
    return [node.guid for node in collisions]
  def create_edges(self):
    for node in self.node_dict.values():
      if node.geom_info != None:
        node.near = [self[guid] for guid in self.bvh_query(node.geom_info["bbox"])
                    if guid != node.guid]
  def get_connections(self,guid):
    node = self[guid]
    connections = [guid + "//" + node_n.guid for node_n in node.near
                   if node_n.guid != guid]
    return connections
  def loop_detection(self, guid, max_depth):
    node = self[guid]
    return loop_detecton(node, max_depth)
  def merge_adjacent(self, guid):
    node = self[guid]
    return merge(node)
  def merge_by_type(self, ifc_type):
    dict = {}
    merged = set()
    guids = [key for key,value in self.items() if value.geom_type == ifc_type]
    for guid in guids:
      if guid not in merged:
        results = merge(self[guid])
        for result in results:
          merged.add(result)
        if len(results) > 1:
          dict[guid] = results
    return dict
  def gjk_query(self,guid1, guid2):
    node1 = self[guid1]
    node2 = self[guid2]
    t_planes1 = get_triangulated_planes(node1)
    t_planes2 = get_triangulated_planes(node2)
    collisions = []
    for plane1 in t_planes1:
        for plane2 in t_planes2:
            if collision.check_tolerance(plane1,plane2,0.01):
              print("Points are identical/ within tolerance")
            else:
              if collision.gjk(plane1, plane2):
                print("3D Collision Detected")
              else:
                print("No Collision")
                # collisions.add(tuple(map(tuple,plane1)))
                # collisions.add(tuple(map(tuple,plane2)))
    return collisions
  #for mattias testing
  def simplify_wall(self):
    result = {}
    walls = [node for node in self.node_dict.values() if node.geom_type == "IfcWall"]
    for wall in walls:
      if wall.geom_info != None:
        continue
      if wall.guid in result:
        continue
      result[wall.guid] = 1
      route = deque([wall])
      subset = []
      while route:
        wall = route.popleft()
        subset.append(wall)
        base = get_base_curve(wall)
        vs = np.array([base[1]- base[0],base[2] - base[1]])
        vs = vs[np.argsort(np.linalg.norm(vs, axis = 1))]
        for e in wall.near:
          if e.geom_info == "IfcWall":
            base_n = get_base_curve(e)
            shared_vertex = np_intersect_rows(base, base_n)
            if len(shared_vertex) != 2:
              continue
            vector_shared = shared_vertex[1] - shared_vertex[0]
            #longer side is the same as vector formed by the shared vertex
            if np.isclose(vs[1]- vector_shared, 0, atol = 1e-5):
              route.append(e)
              subset.append(e)
      for node in subset:
        result[node.guid] = subset
      subset = []

            # I assume they are striaht extrusions for now
          # Check if they share 2 vertex in both top and base curve ? 
    return
  @classmethod
  def create(cls, root):
    cls = cls(root.GlobalId)
    for node in bfs_traverse(root, list_contained_elements = True,func = write_to_node):
      if node!= None:
        cls[node.guid] = node
    cls.get_bbox()
    print("Graph created")
    return cls
class Node:
  def __init__(self, name, _type, guid, geom_info, psets) :
    self.name = name
    self.geom_type = _type
    self.geom_info = geom_info
    self.guid = guid
    self.psets = psets
    self.near = []

  def intersect(node1,node2):
    bbox1 = node1.geom_info["bbox"]
    bbox2 = node2.geom_info["bbox"]
    return collision.intersect(bbox1,bbox2)
  def get_local_coors(self):
    return get_local_coors(self.geom_info["T_matrix"], self.geom_info["vertex"])