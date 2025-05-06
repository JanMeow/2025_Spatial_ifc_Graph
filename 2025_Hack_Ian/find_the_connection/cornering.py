import geometry_processing as GP
import numpy as np
def find_wall_corners(graph):
    """
    Get all the wall to wall connection that are right angled
    This step also assums the previous clustering part is already done that booleans walls in a direction.
    There are poentials for optimization which when we joined the wall initially, we detect both 
    adjacent walls that need boolean operation (walls traversing in the same direction),
    we can memorise those that are not and return them so avoid trversing the whole graph again.
    """
    walls = [value for key,value in graph.node_dict.items() if value.geom_type == "IfcWall"]
    results = {
        "A":[],
        "B":[]
    }
    for wall in walls:
        base_curve_0 = GP.get_base_curve(wall)
        if len(base_curve_0) !=4:
            continue
        if wall.guid not in results["A"] and wall.guid not in results["B"]:
            for near_element in wall.near:
                if near_element.geom_type == "IfcWall":
                    # Get the base curve of the wall
                    base_curve_1 = GP.get_base_curve(near_element)
                    #Skip the ones that are not 3D/ not flat or with weird footing
                    if len(base_curve_1) !=4:
                        continue
                    # Decompose the 2D vectors the vectors returned are already sorted
                    vec_0 = GP.decompose_2D_from_base(base_curve_0)
                    vec_1 = GP.decompose_2D_from_base(base_curve_1)
                    # Check if the two walls are perpendicular to each other here I check only the long side.
                    if np.isclose(np.dot(vec_0[1], vec_1[1]), 0, atol=1e-5):
                        results["A"].append(wall.guid)
                        results["B"].append(near_element.guid)
                        break
    return results

def is_dominant_wall(node):
    return True
def scale_wall_to(node0, node1):
    """
    This function takes two nodes and makes the first node the dominant wall.
    We also assume the wall is a 3D wall with 4 points as base.
    we need to check if its already a dominant wall if yes then no need to do anything.
    """
    #Check if node0 is already a dominant wall
    # if is_dominant_wall(node0):
    #     return 
    # Get the base curve of the wall
    base_curve_0 = GP.get_base_curve(node0)
    base_curve_1 = GP.get_base_curve(node1)
    vec_0 = np.array([base_curve_0[1] - base_curve_0[0], base_curve_0[2] - base_curve_0[0]])
    vec_1 = np.array([base_curve_1[1] - base_curve_1[0], base_curve_1[2] - base_curve_1[0]])
    scalars_0 = np.linalg.norm(vec_0, axis=1)
    scalars_1 = np.linalg.norm(vec_1, axis=1)
    sort_indices_0 = np.argsort(scalars_0, axis = 1)
    sort_indices_1 = np.argsort(scalars_1, axis = 1)
    #Sort the vectors and scalars
    vec_0 = vec_0[sort_indices_0]
    vec_1 = vec_1[sort_indices_1]
    scalars_0 = scalars_0[sort_indices_0]
    scalars_1 = scalars_1[sort_indices_1]
    # Scale up the dominat wall to include the width of the other wall
    scale_vec_0 = vec_0[1]/scalars_0[1]
    S0 = np.eye(3) + ((scalars_0[1] + scalars_1[0])/scalars_0[1] - 1) * np.outer(scale_vec_0, scale_vec_0)
    V0_scaled = node0.geom_info["vertex"] @ S0.T
    # Scale down the other wall to remove the width of the dominant wall
    scale_vec_1 = vec_1[1]/scalars_1[1]
    S1 = np.eye(3) + ((scalars_0[1] + scalars_1[0])/scalars_1[1]) * np.outer(scale_vec_1, scale_vec_1)
    V1_scaled = node1.geom_info["vertex"] @ S1.T

    return V0_scaled, V1_scaled
    