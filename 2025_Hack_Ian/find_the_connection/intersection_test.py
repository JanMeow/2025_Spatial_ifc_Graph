import numpy as np
from utils import get_geometry_info
import ifcopenshell
import multiprocessing
# ====================================================================
# Previous detection to see if an object embed another
# ====================================================================
def get_intersection(entity1, entity2):
    # Get the geometry information
    arr1 = get_geometry_info(entity1, True)[1]
    arr2 = get_geometry_info(entity2, True)[1]

    arr1_view = arr1.view([('', arr1.dtype)] * arr1.shape[1])  # Convert rows to structured dtype
    arr2_view = arr2.view([('', arr2.dtype)] * arr2.shape[1])  # Convert rows to structured dtype
    intersection = np.intersect1d(arr1_view, arr2_view)  # Find intersecting rows
    return intersection.view(arr1.dtype).reshape(-1, arr1.shape[1])
# ====================================================================
# Loop Detection for corner
# ====================================================================
def loop_detecton(node, max_depth=3):
    route_dict = {}
    memory = [None] * (max_depth)

    # Example
    dict_ = {

        "A":[[ "B", "C", "A"],
             ["B", "D", "A"],
            ["C2", "B", "A"]],
    }

    def dfs(node, depth =0, root = None, prev = None, memory = memory):

      # Stop if it exceeds bound
      if depth >= max_depth:
        if root in [node.guid for node in node.near]:
          memory[depth-1] = node.guid
          insertion = memory[:] 
          route_dict[root].append(insertion)
        return
      # Get the current node
      key = node.guid
      # Rmb the root
      if prev == None:
        root = key
        route_dict[root] = []
      else:
        memory[depth-1] = key
      # Begin traversal
      print(memory)
      for near in node.near:
        if near.guid != prev:
          dfs(near, depth = depth +1, root = root, prev = key, memory = memory)

    dfs(node)


    return route_dict
# ====================================================================
# BVH tree from library but not reliable
# ====================================================================
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