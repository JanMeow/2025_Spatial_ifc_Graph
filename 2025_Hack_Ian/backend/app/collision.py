import numpy as np 
from sklearn.decomposition import PCA
from scipy.linalg import lu
from scipy.optimize import linear_sum_assignment
from scipy.spatial import ConvexHull
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
def intersect(bbox1,bbox2, tolerance = 0.05):
    c1 = bbox1[0] - bbox2[1] 
    c2 = bbox1[1] - bbox2[0]
    # Tolerance problem
    m1 = np.isclose(c1, 0, atol=tolerance)
    m2 = np.isclose(c2, 0, atol=tolerance)
    c1[m1] = 0
    c2[m2] = 0
    return np.all(c1 <= 0) and np.all(c2 >= 0)
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
def create_convex_hull(vertices):
    """
    Compute the convex hull of a set of vertices.
    Only need it for concave shape, if the return is the same as the input, 
    then the input shape is already convex
    """
    hull = ConvexHull(vertices)
    return vertices[hull.vertices]
def convex_hull_best_face(faces, vertices):
    """
    Compute the best face to use for the convex hull of a set of vertices.
    The best face is the one that minimizes the spread of the projected vertices.
    """
    # Calculte the U,V and normal N vectors for each face
    U = faces[:,1] - faces[:,0] 
    V = faces[:,2] - faces[:,0]  
    U /= np.linalg.norm(U)
    V /= np.linalg.norm(V)
    N = np.cross(U, V)
    N /= np.linalg.norm(N)
    face_axes = np.stack([U, V, N], axis=1)  
    # Project vertices onto each face and on each axis (U,V,N)
    M = face_axes @ vertices.T
    # Get the variances of the projection for each face 
    V = np.var(M, axis = 2)
    # Get the face that minimizes the variance across 3 axis
    var_sum = V[:, 0] * V[:, 1] * V[:,2] 
    best_face = faces[np.argmin(var_sum)]
    return best_face
def check_pca_similarity(node1_p_axes, node2_p_axes, atol = 0.1, method = "Hungarian"):
    """
    Check if the PCA axes of two objects are similar from PCA 
    Two methods for checking:
    1. Hungarian (Recommended): Slightly slower but more precise, can accept up to 1e-5
    2. Gaussian: Faster but less precise, can accept up to 1e-2
    """
    M = node1_p_axes @ node2_p_axes.T
    similarity = np.abs(M) 
    if method == "Hungarian":
        row_ind, col_ind = linear_sum_assignment(-similarity)
        return np.allclose(similarity[row_ind, col_ind], 1.0, atol=atol)
    if method == "Gaussian":
        _, similarity = lu(similarity, permute_l=True)
        similarity[similarity <atol] = 0
        identity_check = np.allclose(similarity, np.eye(M.shape[0]), atol= atol)
        return identity_check
def oobb_pca(vertices, n_components=3):
    pca = PCA(n_components=n_components)
    pca.fit(vertices)
    # Principal axes (columns are the basis vectors)
    principal_axes = pca.components_
    # Transform points to PCA-aligned space
    transformed_points = vertices @ principal_axes.T
    # Compute bounding box in PCA space
    min_bounds = np.min(transformed_points, axis=0)
    max_bounds = np.max(transformed_points, axis=0)
    # Create 8 corners of the bounding box in PCA space
    box_corners_pca = np.array([
        [min_bounds[0], min_bounds[1], min_bounds[2]],
        [min_bounds[0], min_bounds[1], max_bounds[2]],
        [min_bounds[0], max_bounds[1], min_bounds[2]],
        [min_bounds[0], max_bounds[1], max_bounds[2]],
        [max_bounds[0], min_bounds[1], min_bounds[2]],
        [max_bounds[0], min_bounds[1], max_bounds[2]],
        [max_bounds[0], max_bounds[1], min_bounds[2]],
        [max_bounds[0], max_bounds[1], max_bounds[2]],
    ])
    # Transform corners back to the original space
    box_corners_world = box_corners_pca @ principal_axes  # Reverse transformation  
    return box_corners_world, principal_axes, np.vstack((min_bounds, max_bounds))
def ooBB_convex_hull(faces,vertices):
    return
def create_OOBB(node, method, n_components=3):
    vertices = node.geom_info["vertex"]
    fv_index = node.geom_info["face"]
    faces = vertices[fv_index]
    if method == "PCA":
        return oobb_pca(vertices) 
    if method == "ConvexHull":
        best_face = convex_hull_best_face(faces, vertices)
    
        O = best_face[0]
        U = best_face[1] - O
        V = best_face[2] - O

        U /= np.linalg.norm(U)
        V /= np.linalg.norm(V)
        N = np.cross(U, V)
        N /= np.linalg.norm(N)
        v_O = vertices - O

        local_coords = np.column_stack([np.dot(v_O, U), np.dot(v_O, V)])
        UV_extent = np.vstack((np.min(local_coords, axis=0),
                               np.max(local_coords, axis=0)))

        UV_corners = np.array([
            [UV_extent[0][0], UV_extent[0][1]],  # Bottom-left
            [UV_extent[0][0], UV_extent[1][1]],  # Top-left
            [UV_extent[1][0], UV_extent[0][1]],  # Bottom-right
            [UV_extent[1][0], UV_extent[1][1]]   # Top-right
        ])

        bounding_box_base = UV_corners @ np.stack([U, V], axis=0) + O


        return np.vstack((best_face[0],best_face[1],best_face[2],bounding_box_base)), np.stack([U, V, N], axis =1)