import numpy as np
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape
from collections import deque

# Helper functions
# ====================================================================
def bfs_traverse(base_node, list_contained_elements = True, func = None):

  queue = deque([base_node])
  depth = 0
  result = []

  while len(queue) !=0 :

    current_node = queue.popleft()
    print(f"CURRENT DEPTH : {depth} [TYPE] {current_node.is_a()} [GUID] ({current_node.GlobalId}) [NAME] {current_node.Name}")


    # if hasattr(current_node, "PredefinedType"):
    #   print(f"Predefined Type: {current_node.PredefinedType}")

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



def get_geometry_info(entity, get_global = False):


  result = None
  if hasattr(entity, "Representation"):
    if entity.Representation != None:
      settings = ifcopenshell.geom.settings()
      shape = ifcopenshell.geom.create_shape(settings, entity)

    
      T_matrix = ifcopenshell.util.shape.get_shape_matrix(shape)
      vertex  = ifcopenshell.util.shape.get_vertices(shape.geometry)
      faceVertexIndices = ifcopenshell.util.shape.get_faces(shape.geometry)

      result = [T_matrix, np.around(vertex,2), faceVertexIndices]

      if get_global:
        ones = np.ones(shape = (vertex.shape[0],1))
        stacked = np.hstack((vertex, ones))
        global_coor = stacked@ T_matrix.T
        global_coor = np.around(global_coor[:,0:-1],2)

        result[1] = global_coor

  return result

def write_to_node(current_node):
  if current_node != None:
    geom_infos = get_geometry_info(current_node, get_global = True)

    if geom_infos != None:
      psets = ifcopenshell.util.element.get_psets(current_node)
      node = Node(current_node.Name, current_node.is_a(), current_node.GlobalId, geom_infos[-1], psets)

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
  def __init__(self) :
    self.node_dict = {}

  def __len__(self):
        return len(self.node_dict)

class Node:
  def __init__(self, name, _type, guid, geom_info, psets) :
    self.name = name
    self.geom_type = _type
    self.geom_info = geom_info
    self.guid = guid
    self.psets = psets
    self.near = []  