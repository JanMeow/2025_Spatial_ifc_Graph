import numpy as np
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape
from collections import deque

# Tree Traversal
# ====================================================================
def bfs_traverse(base_node, list_contained_elements = True, func = None):
  queue = deque([base_node])
  depth = 0
  result = []
  while len(queue) !=0 :
    current_node = queue.popleft()
    print(f"CURRENT DEPTH : {depth} [TYPE] {current_node.is_a()} [GUID] ({current_node.GlobalId}) [NAME] {current_node.Name}")

    if func:
      result.append(func(current_node))

    if hasattr(current_node, "ContainsElements") and len(current_node.ContainsElements) != 0:

      for element_rel in current_node.ContainsElements:
        print(f"Contained Elements: {len(element_rel.RelatedElements)}")
        if list_contained_elements:
          for child_element in element_rel.RelatedElements:
            queue.append(child_element)

    if hasattr(current_node, "IsDecomposedBy") and len(current_node.IsDecomposedBy) != 0:
      depth +=1
      for child_rel in current_node.IsDecomposedBy:
        print(f"Number of child: {len(child_rel.RelatedObjects)}")
        for child_obj in child_rel.RelatedObjects:
          queue.append(child_obj)

  print("Function ended, No more spatial child")
  return result


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

def get_planes(entity, get_global = True):
    geom_info =  get_geometry_info(entity, get_global)
    vertex = geom_info[1]
    vertex_indices = geom_info[2]

    arr_shape = (vertex_indices.shape[0], vertex_indices.shape[1], vertex.shape[1])
    array = np.zeros(arr_shape, dtype = np.float32)
    for i,index in enumerate(vertex_indices):
        A, B, C = vertex[index[0]], vertex[index[1]], vertex[index[2]]
        v_stack = np.vstack((A,B,C))
        array[i] = v_stack
        # plane = get_triangulated_equation(A, B, C)
    return array



# Graph Helper Functions
# ====================================================================
def write_to_node(current_node):
  if current_node != None:
    geom_infos = get_geometry_info(current_node, get_global = True)
    if geom_infos != None:
      psets = ifcopenshell.util.element.get_psets(current_node)
      node = Node(current_node.Name, current_node.is_a(), current_node.GlobalId, geom_infos, psets)
      return node

def create_graph(root):
  graph = Graph()
  for node in bfs_traverse(root, True,write_to_node):
    if node!= None:
      graph.node_dict[node.guid] = node
  return graph


# Class Definition for Graph and Node 
# ====================================================================
class Graph:
  def __init__(self,root):
    self.root = root
    self.node_dict = {}
    self.bbox = get_bbox(self)

  def __len__(self):
        return len(self.node_dict)
  
  def get_bbox(self):
    arr = np.zeros((2,3))
    for node in self.node_dict.values():
      if node.geom_info != None:
        arr = np.vstack((arr, node.geom_info["bbox"]))
    max = np.max(arr[1:,:], axis = 0)
    min = np.min(arr[1:,:], axis = 0)
    return np.vstack((min,max))
  
  @classmethod
  def create(cls, root):
    cls = cls(root)
    for node in bfs_traverse(root, True,write_to_node):
      if node!= None:
        cls.node_dict[node.guid] = node
    return cls

class Node:
  def __init__(self, name, _type, guid, geom_info, psets) :
    self.name = name
    self.geom_type = _type
    self.geom_info = geom_info
    self.guid = guid
    self.psets = psets
    self.near = []  