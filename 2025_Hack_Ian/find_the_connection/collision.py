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
def get_center(bbox):
    return (bbox[0] + bbox[1])/2
def envelop(bbox1, bbox2):
    b1 = np.all(bbox1[0]>=bbox2[0]) and np.all(bbox1[1]<=bbox2[1]) 
    b2 = np.all(bbox1[0]<= bbox2[0]) and np.all(bbox1[1]>=bbox2[1])
    return b1 or b2
# ====================================================================
# Mid Phase Collision Detection: OOBB Object Oritend BoundingBox
# ====================================================================


# ====================================================================
# Narrow Phase Collision Detection1: GJK
# ====================================================================
# 0.Initial Direction to avoide degenerate
def compute_centroid(shape):
    return np.mean(shape, axis=0)

def initial_direction_from_centroids(shape1, shape2):
    centroid1 = compute_centroid(shape1)
    centroid2 = compute_centroid(shape2)
    direction = centroid1 - centroid2
    
    if np.allclose(direction, 0, atol=1e-6):  
        bbox_min = np.min(shape1, axis=0)
        bbox_max = np.max(shape1, axis=0)
        return bbox_max - bbox_min  # Default fallback

    return direction
# 1. Get support function
def support(shape, direction):
    return max(shape, key = lambda pt: np.dot(pt,direction))
# 2. Minknowsi Difference
def minkownsi_support(shape1, shape2, direction):
    return support(shape1, direction) - support(shape2, -direction)
# 3. Find triple Product
def triple_product(a,b,c):
    return np.cross(np.cross(b,c),a)
# 4. Check if the simplex formed within the convex Hull contains (0,0)
def contain_origin(simplex, direction):
    if len(simplex) == 2:
        A, B = simplex
        AB = B - A
        AO = -A  

        if np.dot(AB, AO) > 0:
            direction[:] = triple_product(AB, AO, AB)  # New perpendicular direction
        else:
            simplex.pop()  # Remove B, keep A
            direction[:] = AO  # New direction towards origin
        return False

    elif len(simplex) == 3:
        # Triangle case
        A, B, C = simplex
        AB = B - A
        AC = C - A
        AO = -A  # Vector from A to the origin

        normal = np.cross(AB, AC)  # Triangle normal
        if np.dot(np.cross(normal, AC), AO) > 0:
            simplex.pop(1)
            direction[:] = triple_product(AC, AO, AC)
        elif np.dot(np.cross(AB, normal), AO) > 0:
            simplex.pop(2)
            direction[:] = triple_product(AB, AO, AB)
        else:
            return True  # Origin is within the triangle
    return False
# Actual GJK Algorithm
def gjk(shape1, shape2, max_iter = 20):
    direction = initial_direction_from_centroids(shape1, shape2)
    simplex = [minkownsi_support(shape1, shape2, direction)]
    direction = -simplex[0]
    iter_count = 0

    while iter_count < max_iter:
        iter_count += 1
        new_pt = minkownsi_support(shape1, shape2, direction)
        if np.dot(new_pt,direction) < 0:
            return False
        simplex.append(new_pt)
        if contain_origin(simplex, direction):
            return True 
    print(f"GJK did not converge trying miniB")
    mini_BVH(shape1, shape2)
    return False
# Note that if the input are the same, meaning two triangle are overlapping
# GJK might not converge so need to add a check before that
def check_tolerance(shape1, shape2, tolerance = 0.01):
    collisions = []
    for p1 in shape1:
        for p2 in shape2:
            if np.allclose(p1, p2,atol= tolerance):  # Check for exact overlap
                collisions.append(tuple(p1))
    if len(collisions) ==1:
        print("Point Collision Detected")
        return True
    if len(collisions) == 2:
        print("Edge Collision Detected")
        return True
    if len(collisions) == 3:
        print("Face Collision Detected")
        return True
    return False
# Second Narrow Phase Collision Detection
# MiniB, since all the mesh are triangulated, we could also test which triangle intersects using its
# smaller bounding box
def mini_BVH(shape1, shape2):
    bbox1 = get_bbox(shape1)
    bbox2 = get_bbox(shape2)
    if intersect(bbox1,bbox2):
        print("intersection at triangle")
    else:
        print("No intersection")
    return 
# ====================================================================
# Narrow Phase Collision Detection1: SAT
# SAT works faster with triangle
# ====================================================================
def SAT(shape1, shape2):    return