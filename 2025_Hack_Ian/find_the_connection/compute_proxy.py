
import numpy as np
import geometry_processing as GP
import collision as C
from scipy.optimize import linear_sum_assignment
from collections import Counter

# Compute the apropriate type of the element based on the geometry and the position of the element
# ====================================================================
"""
    ### Two step classification apporach
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
Intrinsic_features= {
    "AABB_X_Extent": float,
    "OOBB_X_Extent": float,
    "AABB_Y_Extent": float,
    "OOBB_Y_Extent": float,
    "AABB_Z_Extent": float,
    "OOBB_Z_Extent": float,
    "AABB_base_area": float,
    "OOBB_Base_area": float,
    "Global_X_Extent": float,
    "Global_Y_Extent": float,
    "Global_Z_Extent": float,
    "rel_x_y,z_position_in_the_model/building":float, #lineary dependent on other features
    "z_axis_aligned": bool,
    "number_of_vertices_in_base": int,
    # ==================================
    # Can kind of approximate this by extending the bounding box volume by typical floor height
    # and then computing the relative position to the building?
    "relative_position_to_storey": float, #problem could be some ifc models dont even have building, are there alternatives?
    # We assume that we have one building for now, if not can run some clusterning alogoithm to determine how many buildings are there ?
    "relative_position_to_building": float, #problem could be some ifc models dont even have building, are there alternatives?
}
Contextural_features2 = {
    "upper": "ifctype",
    "lower": "ifctype",
    "left": "ifctype",
    "right": "ifctype",
    "number_of_neighbours_of_same_type": int,
    "variances of the direct neighbours cp": float, # not sure
    "cluster_size":int,
    "cluster_cp_distribution": float, 
    "horizontal_relatives": list[str("ifctype")], # python counter of dict
    "vertical_relatives": list[str("ifctype")],
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
    """
    node = graph[guid]
    # PCA
    principal_axes, min_max_extents= get_oobb(node)
    node.principal_axes = principal_axes
    # Test if the element is z aligned (roof are often not z aligned)
    z_axis_aligned = is_z_axis_aligned(node, atol = 1e-2)
    # Get the base vertex number and area
    number_of_vertices_in_base, AABB_base_area = get_base_info(node)
    OOBB_base_area = np.around(min_max_extents[0] * min_max_extents[1], round_to)
    # Get the relative position to the building and to the floor
    get_relative_position_to_building(graph, node)
    return 
def get_contextural_features(graph, guid):
    node = graph[guid]
    # Get Neighbours
    upper,lower,left,right = assign_neighbours(node)
    # Get number of neighbours of same type
    number_of_neighbours_of_same_type = len([n for n in node.near if n.geom_type == node.geom_type])
    # Get most appeared horizontal neighbours 
    horizontal_relatives = get_horizontal_relatives(graph, node)
     # Test Prints
    print("Upper: ", upper , "Lower: ", lower, "Left: ", left, "Right: ", right)
    return
def get_oobb(node):
    vertex = node.geom_info["vertex"]
    _, principal_axes, min_max_bounds = C.oobb_pca(vertex, n_components=3)
    # Rearange the axis to best match world X,Y,Z axis 
    similarity = np.abs(principal_axes)
    row_ind, col_ind = linear_sum_assignment(-similarity)
    min_max_bounds = min_max_bounds[:,col_ind]
    return similarity[col_ind], min_max_bounds[1] - min_max_bounds[0]
def assign_neighbours(node, atol = 0.01):
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
    elif abs(lower.geom_info["bbox"][0][2] - bbox[0][2]) < atol or lower.guid == node.guid:
        lower = None
    # *** Generally you can not be more left or right than your neighbours ***
    # Exeption is if you are a wall and you encomprises your neighbours aka maybe a window. Here we add a remark
    # in that case, it would return yourself as left or rightneighbour so we just need to test test if the 
    elif left.guid == node.guid:
        left = None
    elif right.guid == node.guid:
        right = None
    return upper, lower, left, right
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
def get_relative_position_to_building(graph, node):
    world_max = graph.bbox.copy()
    bbox = node.geom_info["bbox"]
    world_extent = world_max[1] - world_max[0]
    bbox_extent = bbox[1] - bbox[0]
    rel_position_to_world = bbox_extent / world_extent
    return rel_position_to_world
    

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
    bvh_query_types = Counter([graph.node_dict[guid].geom_type for guid in bvh_query])
    return bvh_query
def is_z_axis_aligned(node, atol = 1e-2):
    """
    Computes if the element is tilted or not
    """
    if np.isclose(node.principal_axes[2][2],1, atol=atol):
        return True
    return False