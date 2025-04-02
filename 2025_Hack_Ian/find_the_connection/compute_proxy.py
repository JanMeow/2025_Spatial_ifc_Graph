
import numpy as np
import geometry_processing as GP
import collision as C
from scipy.optimize import linear_sum_assignment

# Compute the apropriate type of the element based on the geometry and the position of the element
# ====================================================================
"""
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

    feature = {
    upper,
    lower,
    left,
    right,
    OOBB_X_Extent,
    OOBB_Y_Extent,
    OOBB_Z_Extent,
    align_to_z_axis: 0 or 1,
    number of vetices in the base,
    area of the base,
    is_tilted: 0 or 1

    }
    """
def get_features_for_compute(node):
    principal_axes, min_max_bounds = get_oobb(node)
    upper,lower,left,right = assign_neighbours(node, principal_axes)
    print("Upper: ", upper.guid, "Lower: ", lower.guid, "Left: ", left.guid, "Right: ", right.guid)
    return

def get_oobb(node):
    vertex = node.geom_info["vertex"]
    _, principal_axes, min_max_bounds = C.oobb_pca(vertex, n_components=3)
    # Rearange the axis to best match world X,Y,Z axis 
    similarity = np.abs(principal_axes @ np.eye(3).T)
    row_ind, col_ind = linear_sum_assignment(-similarity)
    return similarity[row_ind], min_max_bounds

def assign_neighbours(node, principal_axes):
    """
    1. Get the upper, lower, left, right neighbours of an element based on comparing centre point
    """
    O = GP.get_centre_point(node.geom_info["bbox"])
    cps = np.array([GP.get_centre_point(node.geom_info["bbox"]) for node in node.near])
    bbox_arrays = np.array([node.geom_info["bbox"] for node in node.near])
    # Get the upper, lower,by measuring the AABB corners
    upper = node.near[np.argmax(bbox_arrays[:, 1, 2])]
    lower = node.near[np.argmin(bbox_arrays[:, 0, 2])]
    # Get the left, right neighbours, in fact, left or right doesnt matter but tne most left and right does so we assign one of them
    scalars = np.linalg.norm(principal_axes, axis=1)
    horizontal_direction = principal_axes[np.argmax(scalars)]
    projection = (cps - O) @ horizontal_direction.T
    left = node.near[np.argmin(projection)]
    right = node.near[np.argmax(projection)]
    return upper,lower,left,right

def assign_proxy_type(node):
    return
def compute_relative_position(node):
    """
    1. Compute the relative positon of an element to its neighbour
    2. Compute the relative positon of an element to the building
    3. Compute the relative position of an element to others on the same floor
    """
    return
def compute_absolute_position(graph, node):
    """
    Computes the absolute position of an element to all oter elements
    """
    bbox_G = graph.bvh.bounding_box
    bbox_N = node.geom_info["bbox"]
    return
def is_tilted(node):
    """
    Computes if the element is tilted or not
    """
    vertex = node.geom_info["vertex"]
    if not GP.align_to_axis(vertex, axis=2):
        # calculate the angle between the normal of the face and the z axis

        return 
    return 0