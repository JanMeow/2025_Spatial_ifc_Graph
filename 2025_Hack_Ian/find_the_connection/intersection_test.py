import numpy as np
from utils import get_geometry_info
import ifcopenshell
import multiprocessing

def get_intersection(entity1, entity2):
    # Get the geometry information
    arr1 = get_geometry_info(entity1, True)[1]
    arr2 = get_geometry_info(entity2, True)[1]

    arr1_view = arr1.view([('', arr1.dtype)] * arr1.shape[1])  # Convert rows to structured dtype
    arr2_view = arr2.view([('', arr2.dtype)] * arr2.shape[1])  # Convert rows to structured dtype
    intersection = np.intersect1d(arr1_view, arr2_view)  # Find intersecting rows
    return intersection.view(arr1.dtype).reshape(-1, arr1.shape[1])


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
    print(array)
    # print(linalg.solve)


def loop_detecton(node, max_depth=3):
    route_dict = {}
    memory = [None] * (max_depth)

    # Example
    dict_ = {

        "A":[[ "B", "C", "A"],
             ["B", "C", "D"],
            ["C2", "B", "A"]],
    }

    def dfs(node, depth =0, root = None, prev = None, memory = memory):

      # Stop if it exceeds bound
      if depth >= max_depth:
        if root in [node.guid for node in node.near]:
          insertion = memory[:-1] + [root] 
          route_dict[root].append(insertion)
        return
      # Get the current node
      key = node.guid
      # rmb the root
      if prev == None:
        root = key
        route_dict[root] = []
      else:
        memory[depth-1] = key

      print(memory)
      for near in node.near:
        if near.guid != prev:
            dfs(near, depth = depth +1, root = root, prev = key, memory = memory)

    dfs(node)


    return route_dict

# Library methods which I will replace soon
def get_adjacent(model, entity, tolerance = 0.001):
  # Query neighboruing elements using BVH
  # setup BVH tree
  tree_settings = ifcopenshell.geom.settings()
  iterator = ifcopenshell.geom.iterator(
      tree_settings, model
  )

  assert iterator.initialize()
  t = ifcopenshell.geom.tree()

  while True:
      t.add_element(iterator.get_native())
      # shape = iterator.get()
      if not iterator.next():
          break

  result = t.select(entity,  extend=tolerance)

  adj_guid = [connection.GlobalId for connection in result if connection.GlobalId != entity.GlobalId]

  return adj_guid


def get_direct_connection(entity, graph):
  search_key = entity.GlobalId

  node = graph.node_dict[search_key]
  string1 = node.psets["Cadwork3dProperties"]["BTA TYP"]
  connections = [string1 + "//" + graph.node_dict[node.guid].psets["Cadwork3dProperties"]["BTA TYP"] for node in node.near]
  highlights = [graph.node_dict[node.guid].guid for node in node.near]

  return connections,highlights
