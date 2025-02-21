import numpy as np 
"""
Collision Testing involve 3 algorithms:

1.Broad-Phase Collision Detection
    BVH (Bounding Volume Hierarchy: Testing the b-box of the object)
2.Convex Decomposition for Non-Convex Shapes
    if True in 1, and if the object is concave shape, then break it down to a subset of convex shapes 
i.e, triangle but since the inputs are triangulated so we dont have to do this step 
Note also GJK works on convex shape only because of the support function calculation
3.Narrow-Phase Collision Detection (GJK)
    Since object are triangulated (need to check or enforce export policy), GJK is applied on each triangle
4.EPA (Expaning Polytope Algorithm: Find the closest point between two convex shapes)
"""


# ====================================================================
# Borad phase Collision Detection
# ====================================================================
def build_bvh(sorted_nodes):
    if len(sorted_nodes) == 1:
        return sorted_nodes[0]
    if len(sorted_nodes) == 0:
        return None
    mid = len(sorted_nodes)//2
    node = sorted_nodes[mid]

    node.bvh_left = build_bvh(sorted_nodes[:mid])
    node.bvh_right = build_bvh(sorted_nodes[mid+1:])
    return node
def intersect(bbox1,bbox2):
    
    return all([np.all(bbox1[0] <= bbox2[1]) and np.all(bbox1[1] >= bbox2[0])])

# ====================================================================
# Narrow Phase Collision Detection
# ====================================================================