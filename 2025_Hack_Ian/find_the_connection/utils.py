import numpy as np
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape
import collision
import math
from traversal import bfs_traverse, loop_detecton
from geometry_processing import decompose_2D, angle_between
# ====================================================================
# Geometry Processing
# ====================================================================
def get_bbox(arr):
  max = np.max(arr, axis = 0)
  min = np.min(arr, axis = 0)
  return np.vstack((min,max))
def get_geometry_info(entity, get_global = False):
  if hasattr(entity, "Representation"):
    if entity.Representation != None:
      result = {
        "T_matrix": None,
        "vertex": None,
        "faceVertexIndices": None,
        "bbox": None
      }
      try:
        settings = ifcopenshell.geom.settings()
        shape = ifcopenshell.geom.create_shape(settings, entity)
        result["T_matrix"] = ifcopenshell.util.shape.get_shape_matrix(shape)
        result["vertex"]  = np.around(ifcopenshell.util.shape.get_vertices(shape.geometry),2)
        result["faceVertexIndices"] = ifcopenshell.util.shape.get_faces(shape.geometry)

        if get_global:
          vertex = result["vertex"]
          T_matrix = result["T_matrix"]
          ones = np.ones(shape = (vertex.shape[0],1))
          stacked = np.hstack((vertex, ones))
          global_coor = stacked@ T_matrix.T
          global_coor = np.around(global_coor[:,0:-1],2)
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
    vertex_indices = geom_info["faceVertexIndices"]

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
def merge_test(node, geom_type = None, geom_info = None, v1 = None, l1 = None, tolerance = 0.01):
  """
    Condition of merging for two nodes (wall)
    1. Same Geometry Type
    2. Same Z location to start
    3. Same height a
    4. Same width base curve
    6. Same direction of traversal 
    6. Same Psets #not done yet

    roof:
    #need OBB
    1. test upper plane the same
    2. same thickness
  """
  v2,l2 = decompose_2D(node)
  bbox1 = geom_info["bbox"]
  bbox2 = node.geom_info["bbox"]
  height1 = bbox1[1][2] - bbox1[0][2]
  height2 = bbox2[1][2] - bbox2[0][2]
  angle = angle_between(v1[1], v2[1])

  if geom_type == "IfcWall":
    conditions =[
      geom_type == node.geom_type,
      abs(bbox1[0][2] - bbox2[0][2] )< tolerance,
      abs(height1 - height2) < tolerance,
      abs(l1[0] - l2[0]) < tolerance,
      angle < tolerance or angle - math.pi < tolerance]
  elif geom_type == "IfcSlab":
    conditions = [
      geom_type == node.geom_type,
      abs(bbox1[0][2] - bbox2[0][2] )< tolerance,
      abs(height1 - height2) < tolerance]
  elif geom_type == "IfcRoof":
    conditions = [
      geom_type == node.geom_type
  ]
  if all(conditions):
    return True
  return False
def merge(node):
  memory= {
    "T": set(),
    "F": set()
  }
  _type = node.geom_type
  geom_info = node.geom_info
  v,l = decompose_2D(node)
  stack = [node]
  while stack:
    current = stack.pop()
    memory["T"].add(current.guid)
    for node_n in current.near:
      if node_n.guid not in memory["T"] and node_n.guid not in memory["F"]:
        if merge_test(node_n, _type, geom_info, v, l):
          stack.append(node_n)
        else:
          memory["F"].add(node_n.guid)
  return list(memory["T"])
def write_to_node(current_node):
  if current_node != None:
    geom_infos = get_geometry_info(current_node, get_global = True)
    if geom_infos != None:
      psets = ifcopenshell.util.element.get_psets(current_node)
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
  def get_connections(self,guid):
    node = self.node_dict[guid]
    connections = [guid + "//" + node_n.guid for node_n in node.near
                   if node_n.guid != guid]
    return connections
  def loop_detection(self, guid, max_depth):
    node = self.node_dict[guid]
    return loop_detecton(node, max_depth)
  def merge_adjacent(self, guid):
    node = self.node_dict[guid]
    return merge(node)
  def gjk_query(self,guid1, guid2):
    node1 = self.node_dict[guid1]
    node2 = self.node_dict[guid2]
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
  @classmethod
  def create(cls, root):
    cls = cls(root.GlobalId)
    for node in bfs_traverse(root, True,write_to_node):
      if node!= None:
        cls.node_dict[node.guid] = node
    cls.get_bbox()
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
