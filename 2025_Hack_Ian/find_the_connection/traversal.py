import numpy as np
import ifcopenshell
import multiprocessing
from collections import deque
# ====================================================================
# ====================================================================
# Tree Traversal
# ====================================================================
def default_print(node, depth):
  print(f"CURRENT DEPTH : {depth} [TYPE] {node.is_a()} [GUID] ({node.GlobalId}) [NAME] {node.Name}")

def bfs_traverse(base_node, list_contained_elements = True, func = None):
  queue = deque([base_node])
  depth = 0
  result = []
  while len(queue) !=0 :
    current_node = queue.popleft()
    default_print(current_node, depth)
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

def dfs_traverse(base_node, list_contained_elements = True, func = None):
  stack = [base_node]
  depth = 0
  result = []
  while len(stack) !=0 :
    current_node = stack.pop()
    default_print(current_node, depth)
    if func:
      result.append(func(current_node))

    if hasattr(current_node, "ContainsElements") and len(current_node.ContainsElements) != 0:
      for element_rel in current_node.ContainsElements:
        print(f"Contained Elements: {len(element_rel.RelatedElements)}")
        if list_contained_elements:
          for child_element in element_rel.RelatedElements:
            stack.append(child_element)
    if hasattr(current_node, "IsDecomposedBy") and len(current_node.IsDecomposedBy) != 0:
      depth +=1
      for child_rel in current_node.IsDecomposedBy:
        print(f"Number of child: {len(child_rel.RelatedObjects)}")
        for child_obj in child_rel.RelatedObjects:
          stack.append(child_obj)
  print("Function ended, No more spatial child")
  return result
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
      for near in node.near:
        if near.guid != prev:
          dfs(near, depth = depth +1, root = root, prev = key, memory = memory)

    dfs(node)

    return route_dict
# ====================================================================
# Slow methods from library for referneces and check
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