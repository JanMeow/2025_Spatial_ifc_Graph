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
# Currently the splitting has a bit of a problem of missing 1-2 collision
# since I sort the list only using the min corner
# ====================================================================
class BVH ():
    def __init__(self, bbox, nodes, leaf = False):
        self.left = None
        self.right = None
        self.leaf = leaf
        self.bbox = bbox
        self.nodes = nodes
def build_bvh(sorted_nodes):
    if len(sorted_nodes) == 1:
        return BVH(sorted_nodes[0].geom_info["bbox"], sorted_nodes[0], leaf = True)
    if len(sorted_nodes) == 0:
        return None
    bbox = get_bbox([node.geom_info["bbox"] for node in sorted_nodes])
    bvh = BVH(bbox, sorted_nodes)
    mid = len(sorted_nodes)//2
    bvh.left = build_bvh(sorted_nodes[:mid])
    bvh.right = build_bvh(sorted_nodes[mid:])
    return bvh
def intersect(bbox1,bbox2):
    return np.all(bbox1[0] <= bbox2[1]) and np.all(bbox1[1] >= bbox2[0])
def get_bbox(bboxs):
    arr = np.vstack(bboxs)
    _min = np.min(arr, axis = 0)
    _max = np.max(arr, axis = 0)
    return np.vstack((_min,_max))
def envelop(bbox1, bbox2):
    b1 = np.all(bbox1[0]>=bbox2[0]) and np.all(bbox1[1]<=bbox2[1]) 
    b2 = np.all(bbox1[0]<= bbox2[0]) and np.all(bbox1[1]>=bbox2[1])
    return b1 or b2
# ====================================================================
# Narrow Phase Collision Detection
# ====================================================================
# 1. Get support function
def support(shape, direction):
    return max(shape, key = lambda pt: np.dot(pt,direction))
# 2. Minknowsi Difference
def minkownsi_support(shape1, shape2, direction):
    return support(shape1, direction) - support(shape2, -direction)
# 3. Find triple Product
def triple_product(a,b,c):
    return np.dot(a,np.cross(b,c))
# 4. Check if the simplex formed within the convex Hull contains (0,0)
def contain_origin(simplex, direction):
    if len(simplex) == 2:
        A,B = simplex
        AB = B-A
        AO = -A
        if np.dot(AB, AO) >0:
            direction[:] = triple_product(AO, AB, AB)
        else:
            simplex[:] = [A]
            direction[:] = AO
        return False
    if len(simplex) == 3:
        A,B,C = simplex
        AB = B-A
        AC = C-A
        AO = -A
        normal = np.cross(AB, AC)

        if np.dot(np.cross(normal, AC), AO) > 0:
            simplex[:] = [A,C]
            direction[:] =triple_product(AC, AO, AC)
        elif np.dot(np.cross(AB, normal), AO) > 0:
            simplex[:] = [A,B]
            direction[:] = triple_product(AB, AO, AB)
        else:
            return True
        return False
# Actual GJK Algorithm
def GJK(shape1, shape2):
    direction = np.array([1,0,0])
    simplex = [minkownsi_support(shape1, shape2, direction)]
    direction = -simplex[0]
    while True:
        new_pt = minkownsi_support(shape1, shape2, direction)
        if np.dot(new_pt,direction) < 0:
            print("No collision detected")
            return False
        simplex.append(new_pt)
        if contain_origin(simplex, direction):
            print("origin in triangle, collision detected")
            return True 