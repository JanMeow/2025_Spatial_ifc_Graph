
import numpy as np
import geometry_processing as GP
import collision as C
from scipy.optimize import linear_sum_assignment
from collections import Counter, defaultdict

# Compute the apropriate type of the element based on the geometry and the position of the element
# ====================================================================
"""
    ### Two step classification apporach
    clasfication label 
    Computes the most possible element type of an ifcProxy element.
    or later extend to seeing if elements are mistyped based on a confidence score
    Below are some observations to generate a criterion:
    1.0 Relative position to the horizontal neighbours
        1.0.1 if the element is between two walls horizontally (approximate), it has a high chance being a wall
        1.0.2 if the element is between two slabs horizontally (approximate), it has a high chance being a slab
    1.1 Relative position to the vertical neighbours
        1.1.1 if the element is between two walls vertically (approximate), it has a high chance being a slab
        1.1.2 if the element is between two slabs vertically (approximate), it has a high chance being a wall
        1.1.3 if the element is between a roof and a slab vertically (approximate), it has a high chance being a wall or a column
        1.1.4 if the element is between two slab vertically (approximate), it has a high chance being a wall or a column
    1.2 Number of neighbourss
        1.2.1 if the element has two horizontal neighbours, it has a high chance being a wall
        1.2.2 if the element has two vertical neighbours, upper being a roof and lower being a slab, it has a high chance being a wall or column
    2. roof: angled, highest in the relative position to the building
    3. slab: flat base area
    4. roof: flat base area, but tilted
    ...
    ...
    ...
    Many of the above observations could be derived to help deduce the nature of an element.
    As such, this module works to formulate an algoirthm to compute the most probable type of an element and apply ML algorithm based on the criterion above.

    We first need to calculate the following features:
    1. Get its upper, lower, left, right neighbours type fill NaN if the neighbour is also proxy, and if no upper neighbout (in the case of roof)
        => assign_neighbours(node)
    2. Get its relative position to the building and to the floor (this might require you to group elements by floor and then by building
    2  as they might not be specifid in the model or the model has a lot of noises e.g, unwanted geometries eg funtirures...)
    2. Whether it is tilted and, maybe how tilted it is.
    3. Likelihood. for example, when we model, we model often multiple walls touching each other, and slabs, so we need to calculate also the 
        their tendecy of clustering.
    4.Proportion of the base curve => determining if its horiozontal or vertical or slanted element => determind_oobb_proportion(node)
    """
# ===================================================================================
# Global Variables for features type and rounding
# ===================================================================================
label_map = {
    "None": 0,
    "IfcWall": 1, #Can further classfy into outer or inner
    "IfcSlab": 2,
    "IfcRoof": 3,
    "IfcColumn": 4,
    "IfcBeam": 5,
    "IfcCurtainWall": 6,
    "IfcFooting": 7,
    "IfcPlate": 8
}

round_to = 2
# ===================================================================================
# ===================================================================================
# ====================================================================
# Compute the features for the element
# ====================================================================
def get_Intrinsic_features(graph, guid):
    """
    The algorithm should also work a bit differently depending on whether there is labelled element
    if there is none, we need to first guess the element not based on the surrounding elements but based on the element itself
    then do it iteratively until it gives the highest confidence score

    *Optimization*:
    Currently uses a O(n) face normal check for otpmization to know if we can skip OOBB check which is O3 
    In the future, can do a sampling for the first 20 meshes to see if over 50% of them are axis aligned
    if yes, then keep the hybrid apporach, if not, then just ignore the check axis aligned and perform PCA directly
    another way is to use the is_xyz_aligned function to check which axis is aligned and then reduce the PCA n_component 

    """
    node = graph[guid]
    world_xyz = graph.bbox
    world_extent = world_xyz[1] - world_xyz[0]
    self_xyz = node.geom_info["bbox"]
    self_extent = self_xyz[1] - self_xyz[0]
    # Surface Area and Volume
    area, largest_normal, largest_face_area, number_of_faces_in_largest_face, volume = get_surface_area_and_volume(node)
    # Check if the largest face is on xy plane or has vertical vector
    if not np.isclose(largest_normal[2], 0 , atol = 1e-2):
        Largest_face_normal_has_Z_vector = True     #0 means horizontal 1 has vertical vector
    else:
        Largest_face_normal_has_Z_vector = False
    # Normalize bounding box
    relative_position_min = (self_xyz[0] - world_xyz[0]) / world_extent
    relative_position_max = (self_xyz[1] - world_xyz[1]) / world_extent
    relative_cp = (GP.get_centre_point(node.geom_info["bbox"]) - world_xyz[0])/ world_extent
    # Check if object is XYZ Axis aligned, if yes no need check PCA 
    is_xyz_aligned, xyz_aligned_count, z_axis_align_count = is_axis_aligned(node, atol = 1e-3, threshold = 0.9)
    number_of_vertices_in_base, AABB_base_area = get_base_info(node)
    # PCA if needed
    if is_xyz_aligned:
        node.principal_axes = np.eye(3)
        node.is_axis_aligned = True
        node.z_axis_aligned = True
        min_max_extents = self_xyz[1] - self_xyz[0]
        OOBB_base_area = AABB_base_area
    else:
        node.is_axis_aligned = False
        principal_axes, min_max_extents= get_oobb(node)
        node.principal_axes = principal_axes
        node.z_axis_aligned = is_z_axis_aligned(node, atol = 1e-2)
        # Get the base vertex number and area
        OOBB_base_area = np.around(min_max_extents[0] * min_max_extents[1], round_to)

    # Features 
    Intrinsic_features= {
    "AABB_X_Extent": node.geom_info["bbox"][1][0] - node.geom_info["bbox"][0][0],
    "OOBB_X_Extent": min_max_extents[0],
    "AABB_Y_Extent": node.geom_info["bbox"][1][1] - node.geom_info["bbox"][0][1],
    "OOBB_Y_Extent": min_max_extents[1],
    "AABB_Z_Extent": node.geom_info["bbox"][1][2] - node.geom_info["bbox"][0][2],
    "OOBB_Z_Extent": min_max_extents[2],
    "AABB_base_area": AABB_base_area,
    "OOBB_Base_area": OOBB_base_area,
    "World_X_Extent": world_extent[0],
    "World_Y_Extent": world_extent[1],
    "World_Z_Extent": world_extent[2],
    "Self_X_Extent": self_extent[0],
    "Self_Y_Extent": self_extent[1],
    "Self_Z_Extent": self_extent[2],
    "Relative_CP_X": relative_cp[0],
    "Relative_CP_Y": relative_cp[1],
    "Relative_CP_Z": relative_cp[2],
    "Relative_position_min_X": relative_position_min[0],
    "Relative_position_min_Y": relative_position_min[1],
    "Relative_position_min_Z": relative_position_min[2],
    "Relative_position_max_X": relative_position_max[0],
    "Relative_position_max_Y": relative_position_max[1],
    "Relative_position_max_Z": relative_position_max[2],
    "Z_axis_aligned": node.z_axis_aligned,
    "Surface_area":area,
    "Volume":volume,
    "Largest_face_area": largest_face_area,
    "Largest_face_normal_has_Z_vector": Largest_face_normal_has_Z_vector,
    "Number_of_vertices_in_base": number_of_vertices_in_base,
    "Number_of_vertices": len(node.geom_info["vertex"]),
    "Number_of_faces": len(node.geom_info["face"]),
    "Number_of_XYZ_aligned_faces": xyz_aligned_count,
    "Number_of_Z_aligned_faces": z_axis_align_count,
    "Number_of_faces_in_largest_face":number_of_faces_in_largest_face
    }
    node.intrinsic_features = Intrinsic_features
    return Intrinsic_features
def get_contextural_features(graph, guid):
    node = graph[guid]
    self_cp = GP.get_centre_point(node.geom_info["bbox"])
    # Get Neighbours
    neighbours = assign_neighbours(node)
    # Get horizontal neighbours and their counts
    Horizontal_relatives = get_horizontal_relatives(graph, node)
    # Get Vertical neighbours
    Vertical_relatives = get_vertical_relatives(graph, node)
    # Get Cluster size and distribution
    cluster = get_cluster(node)
    Cluster_features = get_cluster_features(graph, cluster)
     # Result
    Contextural_features = {
    "upper": neighbours[0],
    "lower": neighbours[1],
    "left": neighbours[2],
    "right": neighbours[3],
    "number_of_neighbours_of_same_type": len([n for n in node.near if n.geom_type == node.geom_type]),
}
    return Contextural_features | Horizontal_relatives| Vertical_relatives| Cluster_features
def get_cluster_features(graph, cluster):
    cluster_bbox, cluster_cp = get_cluster_distribution(cluster)
    # Convert cluster_bbox to relative position in the entire graph
    world_extent = graph.bbox[1] - graph.bbox[0]
    cluster_bbox = (cluster_bbox - graph.bbox[0])/world_extent
    cluster_cp = (cluster_cp - graph.bbox[0])/world_extent
    bboxs = np.stack([node.geom_info["bbox"] for node in cluster], axis =1)
    cps = (bboxs[0] + bboxs[1])/2 
    cps = (cps - graph.bbox[0])/world_extent
    distances_to_cluster_cp = np.linalg.norm(cps - cluster_cp, axis = 1)
    variances_of_distance_to_cluster_cp = np.var(distances_to_cluster_cp)
    # variances of cp coordinate across xyz
    variances_of_cp = np.round(np.var(cps, axis=0), decimals=round_to)
    # variances of orientation
    orientations = np.array([node.principal_axes for node in cluster])
    var_x_orientation = np.linalg.norm(np.var(orientations[:,0], axis=0))
    var_y_orientation  = np.linalg.norm(np.var(orientations[:,1], axis=0))
    var_z_orientation  = np.linalg.norm(np.var(orientations[:,2], axis=0))
    variance_vector = np.array([var_x_orientation, var_y_orientation, var_z_orientation])
    anisotropy_ratio = np.max(variance_vector) / np.min(variance_vector + 1e-8)
    # Mean height, width and depth of the cluster element
    heights = [node.intrinsic_features["OOBB_Z_Extent"] for node in cluster]
    #Longer side is defined as the width of the element and shorter as depth
    oxy = np.array([np.vstack([node.intrinsic_features["OOBB_X_Extent"], 
                               node.intrinsic_features["OOBB_Y_Extent"]
                               ]) for node in cluster])
    sorted_oxy = np.sort(oxy, axis=1)
    widths = sorted_oxy[:,1]
    depths = sorted_oxy[:,0]
    # Cluster features
    cluster_features ={
    "cluster_size": len(cluster),
    "cluster_cp_X": cluster_cp[0],
    "cluster_cp_Y": cluster_cp[1],
    "cluster_cp_Z": cluster_cp[2],
    "cluster_X_start": cluster_bbox[0][0],
    "cluster_X_end": cluster_bbox[1][0],
    "cluster_Y_start": cluster_bbox[0][1],
    "cluster_Y_end": cluster_bbox[1][1],
    "cluster_Z_start": cluster_bbox[0][2],
    "cluster_Z_end": cluster_bbox[1][2],
    "variances_X_of_cp": variances_of_cp[0],
    "variances_Y_of_cp": variances_of_cp[1],
    "variances_Z_of_cp": variances_of_cp[2],
    "variances_of_distance_to_cluster_cp": variances_of_distance_to_cluster_cp,
    "variances_of_orientation_X": np.round(var_x_orientation, decimals=round_to),
    "variances_of_orientation_Y": np.round(var_y_orientation, decimals=round_to),
    "variances_of_orientation_Z": np.round(var_z_orientation, decimals=round_to),
    "anisotropy_ratio": anisotropy_ratio,
    "height_mean": np.mean(heights),
    "height_var": np.var(heights),
    "width_mean": np.mean(widths),
    "width_var": np.var(widths),
    "depth_mean": np.mean(depths),
    "depth_var": np.var(depths),
    "z_alignment_consistency": len([node for node in cluster if node.z_axis_aligned]) / len(cluster),
    }
    return cluster_features
def get_oobb(node):
    vertex = node.geom_info["vertex"]
    _, principal_axes, min_max_bounds = C.oobb_pca(vertex, n_components=3)
    # Rearange the axis to best match world X,Y,Z axis 
    similarity = np.abs(principal_axes)
    row_ind, col_ind = linear_sum_assignment(-similarity)
    min_max_bounds = min_max_bounds[:,col_ind]
    return similarity[col_ind], min_max_bounds[1] - min_max_bounds[0]
def assign_neighbours(node, atol = 0.01, return_type = "geom_type"):
    """
    1. Get the upper, lower, left, right neighbours of an element based on comparing centre point
    2. Compare the neighbours to yourself if you are upper, lower, 
        techeotically you can not be lefter or righter than your  neighbours return None
    """
    bbox = node.geom_info["bbox"]
    O = GP.get_centre_point(bbox)
    principal_axes = node.principal_axes
    neighbours = node.near + [node]
    # Get the centre points of the neighbours and their bounding box
    cps = np.array([GP.get_centre_point(node.geom_info["bbox"]) for node in neighbours])
    bbox_arrays = np.array([node.geom_info["bbox"] for node in neighbours])
    # Get the upper, lower,by measuring the AABB corners
    upper = neighbours[np.argmax(bbox_arrays[:, 1, 2])]
    lower = neighbours[np.argmin(bbox_arrays[:, 0, 2])]
    # Get the left, right neighbours, in fact, left or right doesnt matter but tne most left and right does so we assign one of them
    scalars = np.linalg.norm(principal_axes, axis=1)
    horizontal_direction = principal_axes[np.argmax(scalars)]
    projection = (cps - O) @ horizontal_direction.T
    left = neighbours[np.argmin(projection)]
    right = neighbours[np.argmax(projection)] 
    # Compare the neighbours to yourself if you are upper, lower, left, right
    if abs(upper.geom_info["bbox"][1][2] - bbox[1][2]) < atol or upper.guid == node.guid:
        upper = None
    if abs(lower.geom_info["bbox"][0][2] - bbox[0][2]) < atol or lower.guid == node.guid:
        lower = None
    if left.guid == node.guid:
        left = None
    if right.guid == node.guid:
        right = None
    
    results = [getattr(node, return_type, f"no {return_type} attribute") if node != None else None for node in [upper, lower, left, right]]
    return results
def get_base_info(node):
    vertex = node.geom_info["vertex"]
    face = node.geom_info["face"]
    lowest_z = node.geom_info["bbox"][0][2]
    base_v_idx =np.where(vertex[:,2] == lowest_z)
    base_f_idx = face[np.all(np.isin(face,base_v_idx), axis =1) == True]
    base_f = vertex[base_f_idx]
    number_of_vertices_in_base = len(base_v_idx[0])
    AABB_base_area = 0
    if number_of_vertices_in_base >=3:
        for f in base_f:
            AABB_base_area += GP.get_polygon_area(f)
    return number_of_vertices_in_base, np.round(AABB_base_area, decimals= round_to)
def get_surface_area_and_volume(node):
    v = node.geom_info["vertex"]
    f = node.geom_info["face"].copy()
    # Clean degenerate faces
    normals, orientation, valid_mask = GP.check_orientation_and_clean_degenerate(v, f)
    f= f[valid_mask]
    # Check if the face normals are flipped
    flipped = np.where(orientation <0)[0]
    if len(flipped) > 0:
        f[flipped] = f[flipped][:, [0, 2, 1]]
        # Clean again in case flipping created new degenerate faces
        normals, orientation, valid_mask = GP.check_orientation_and_clean_degenerate(v, f)
        f = f[valid_mask]
    # Save back
    node.geom_info["face"] = f
    node.geom_info["normal"] = normals
    area = GP.triangle_areas(v, f)
    volume = GP.triangle_mesh_volume(v, f)
    normal, largest_face_area, no_of_face = get_largest_face_area(normals, area, precision=round_to)
    return np.sum(area), normal, np.round(largest_face_area, decimals=round_to), no_of_face, volume
def get_largest_face_area(normals, areas, precision=3):
    # Round and convert normals to tuples
    rounded_normals = [tuple(np.round(n, precision)) for n in normals]
    # Sum areas for each unique normal
    area_by_normal = defaultdict(float)
    for normal, area in zip(rounded_normals, areas):
        if normal not in area_by_normal:
            area_by_normal[normal] = []
        area_by_normal[normal].append(area)
    # Get the dominant normal and its area
    normal,area_list = max(area_by_normal.items(), key=lambda v: sum(v[1]))
    # Number of faces in the largest area 
    no_of_face = len(area_list)
    return np.array(normal),sum(area_list),no_of_face
def is_axis_aligned(node, atol=1e-3, threshold=0.9):
    normals = node.geom_info["normal"]
    axis_dirs = np.array([[1,0,0], [0,1,0], [0,0,1],
                          [-1,0,0], [0,-1,0], [0,0,-1]])
    xyz_aligned_count = 0
    z_axis_align_count = 0
    for n in normals:
        if np.any(np.all(np.abs(n - axis_dirs) < atol, axis=1)):
            xyz_aligned_count += 1
        if np.isclose(abs(n[2]) -1,0, atol=atol):
            z_axis_align_count += 1
    ratio = xyz_aligned_count / len(normals)
    return ratio > threshold, xyz_aligned_count, z_axis_align_count 
def get_horizontal_relatives(graph, node, extent = 0.05):
    """
    1. Reduce the bounding box of the element by a scale factor and use this as collision test
        to see what is the most types it hits the counts and the most common type is the one that is the most likely to be the same type as the element.
    """
    world_max = graph.bbox.copy()
    bbox = node.geom_info["bbox"]
    bbox_z_centre = (bbox[1][2] + bbox[0][2]) / 2
    world_max[0][2] = bbox_z_centre -  extent
    world_max[1][2] = bbox_z_centre +  extent

    bvh_query = graph.bvh_query(world_max)
    bvh_query_types = Counter([graph[guid].geom_type for guid in bvh_query])
    return {"HR_"+ k: bvh_query_types[k] for k in label_map.keys()}
def get_vertical_relatives(graph, node, extent = 0.05):
    world_max = graph.bbox.copy()
    bbox = node.geom_info["bbox"]
    bbox_x_centre = (bbox[1][0] + bbox[0][0]) / 2
    bbox_y_centre = (bbox[1][1] + bbox[0][1]) / 2
    world_max[0][0] = bbox_x_centre - extent
    world_max[1][0] = bbox_x_centre + extent
    world_max[0][1] = bbox_y_centre - extent
    world_max[1][1] = bbox_y_centre + extent
    bvh_query = graph.bvh_query(world_max)
    bvh_query_types = Counter([graph[guid].geom_type for guid in bvh_query])
    return {"VR_"+ k: bvh_query_types[k] for k in label_map.keys()}
def get_cluster(node):
    stack = [node]
    cluster = set()
    while stack:
        current = stack.pop()
        cluster.add(current)
        for n in current.near:
            if n.geom_type == current.geom_type and n not in cluster:
                stack.append(n)
    return cluster
def get_cluster_distribution(cluster):
    bboxs = np.vstack([node.geom_info["bbox"] for node in cluster])
    cps = np.array([GP.get_centre_point(bbox) for bbox in bboxs])
    cluster_bbox = np.array((np.min(bboxs, axis=0), np.max(bboxs, axis=0)))
    cluster_cp = GP.get_centre_point(cluster_bbox)
    return cluster_bbox, cluster_cp
def is_z_axis_aligned(node, atol = 1e-2):
    """
    Computes if the element is tilted or not
    """
    if np.isclose(node.principal_axes[2][2],1, atol=atol):
        return True
    return False
def get_rel_position(graph, target_pt):
    world_xyz = graph.bbox
    world_extent = world_xyz[1] - world_xyz[0]
    relative_position = (target_pt - world_xyz[0])/world_extent
    return relative_position
def get_edge_attr_for_GNN(node, neighbour):
    """
    Get the edge attributes for the GNN from the neighbours
    [
        z_diff,
        cp_diff,
        distance_3D,
        volume_ratio,
        height_ratio,
        angle_z,
    ]
    """
    # Get the edge attributes
    bbox0_min, bbox0_max = node.geom_info["bbox"]
    bbox1_min, bbox1_max = neighbour.geom_info["bbox"]
    z_diff = abs(node.geom_info["bbox"][1][2] - neighbour.geom_info["bbox"][0][2])
    cp_z_diff = node.intrinsic_features["Relative_CP_Z"] - neighbour.intrinsic_features["Relative_CP_Z"]
    cp_y_diff = node.intrinsic_features["Relative_CP_Y"] - neighbour.intrinsic_features["Relative_CP_Y"]
    cp_x_diff = node.intrinsic_features["Relative_CP_X"] - neighbour.intrinsic_features["Relative_CP_X"]
    distance_3D = np.linalg.norm(GP.get_centre_point(node.geom_info["bbox"]) - GP.get_centre_point(neighbour.geom_info["bbox"]))
    volume_ratio = node.intrinsic_features["Volume"] / neighbour.intrinsic_features["Volume"]
    height_ratio = node.intrinsic_features["OOBB_Z_Extent"] / neighbour.intrinsic_features["OOBB_Z_Extent"]
    angle_z = np.arccos(np.clip(np.dot(node.principal_axes[2], neighbour.principal_axes[2]), -1.0, 1.0))
    angle_y = np.arccos(np.clip(np.dot(node.principal_axes[1], neighbour.principal_axes[1]), -1.0, 1.0))
    angle_x = np.arccos(np.clip(np.dot(node.principal_axes[0], neighbour.principal_axes[0]), -1.0, 1.0))
    x_overlap = max(0, min(bbox0_max[0], bbox1_max[0]) - max(bbox0_min[0], bbox1_min[0]))
    y_overlap = max(0, min(bbox0_max[1], bbox1_max[1]) - max(bbox0_min[1], bbox1_min[1]))
    z_overlap = max(0, min(bbox0_max[2], bbox1_max[2]) - max(bbox0_min[2], bbox1_min[2]))
    direction_vec = GP.get_centre_point(neighbour.geom_info["bbox"]) - GP.get_centre_point(node.geom_info["bbox"])
    direction_vec /= np.linalg.norm(direction_vec) + 1e-8  # Normalize
    overlap_volume = x_overlap * y_overlap * z_overlap




    return np.array([z_diff, cp_z_diff, cp_y_diff, cp_x_diff, distance_3D, volume_ratio, height_ratio, 
                     angle_z, angle_y, angle_x, x_overlap, y_overlap, z_overlap,
                     direction_vec[0], direction_vec[1], direction_vec[2],
                     overlap_volume])
def get_edge_attr_horizontal_relatives(graph, node, extent = 0.05):
    world_max = graph.bbox.copy()
    bbox = node.geom_info["bbox"]
    node_cp = GP.get_centre_point(bbox)
    bbox_z_centre = (bbox[1][2] + bbox[0][2]) / 2
    world_max[0][2] = bbox_z_centre -  extent
    world_max[1][2] = bbox_z_centre +  extent
    bvh_query = graph.bvh_query(world_max)
    return {guid:get_edge_attr_for_GNN(node, graph[guid])for guid in bvh_query}
def get_edge_attr_get_vertical_relatives(graph, node, extent = 0.05):
    world_max = graph.bbox.copy()
    bbox = node.geom_info["bbox"]
    bbox_x_centre = (bbox[1][0] + bbox[0][0]) / 2
    bbox_y_centre = (bbox[1][1] + bbox[0][1]) / 2
    world_max[0][0] = bbox_x_centre - extent
    world_max[1][0] = bbox_x_centre + extent
    world_max[0][1] = bbox_y_centre - extent
    world_max[1][1] = bbox_y_centre + extent
    bvh_query = graph.bvh_query(world_max)
    return {guid:get_edge_attr_for_GNN(node, graph[guid])for guid in bvh_query}