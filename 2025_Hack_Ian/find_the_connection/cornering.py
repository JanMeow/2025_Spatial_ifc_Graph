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
    walls = [e for e in graph.node_dict.values() if e.geom_type == "IfcWall"]
    results = {}
    for wall in walls:
        base_curve_0 = GP.get_base_curve(wall)
        results[wall.guid] = []
        if len(base_curve_0) !=4:
            continue
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
                # Make sure the have an overlapping point
                intersection = GP.np_intersect_rows(base_curve_0, base_curve_1)
                if len(intersection) == 1:
                    # Check if the two walls are perpendicular to each other here I check only the long side.
                    if np.isclose(np.dot(vec_0[1], vec_1[1]), 0, atol=1e-5):
                        results[wall.guid].append(near_element.guid)
                        
    return results

def return_dominant_wall(node0, node1):
    """
    Check which node is the dominant wall 
    The dominant wall is the one where the intersection point is in the inner side of the wall.
    """
    base_curve_0 = GP.get_base_curve(node0)
    base_curve_1 = GP.get_base_curve(node1)
    centroid = np.mean(np.vstack((base_curve_0, base_curve_1)), axis=0)
    intersection = GP.np_intersect_rows(base_curve_0, base_curve_1)

    vec_0 = GP.decompose_2D_from_base(base_curve_0)
    vec_1 = GP.decompose_2D_from_base(base_curve_1)

    # Test the direction of the vector to make sure it points to the centroid
    centroid_direction = centroid - intersection[0]
    if np.dot(vec_0[0], centroid_direction) < 0:
        vec_0[0] = -vec_0[0]

    var_U = np.dot((base_curve_0 - intersection), vec_0[0])
    # Variances = 0 are the points that are in the same level as the intersection. 
    # The other number if negative means outer, positive means inner.
    if np.sum(var_U) < 0:
        print("Node 0 is the dominant wall")
        return node0
    else:
        print("Node 1 is the dominant wall")
        return node1
    

def make_corner_type_1(node0, node1):
    """
    This function takes two nodes and makes the first node the dominant wall.
    We also assume the wall is a 3D wall with 4 points as base.
    we need to check if its already a dominant wall if yes then no need to do anything.
    """
    #Check if node0 is already a dominant wall
    dominant_wall = return_dominant_wall(node0, node1)
    if dominant_wall == node0:
        print("Node 0 is already the dominant wall")
        return 
    
    base_curve_0 = GP.get_base_curve(node0)
    base_curve_1 = GP.get_base_curve(node1)
    vec_0 = GP.decompose_2D_from_base(base_curve_0)
    vec_1 = GP.decompose_2D_from_base(base_curve_1)
    scalars_0 = np.linalg.norm(vec_0, axis = 1)
    scalars_1 = np.linalg.norm(vec_1, axis = 1)
    # Scale up the dominat wall to include the width of the other wall
    unit_vec_0 = vec_0[1]/scalars_0[1]
    S0 = np.eye(3) + ((scalars_0[1] + scalars_1[0])/scalars_0[1] - 1) * np.outer(unit_vec_0, unit_vec_0)
    V0_scaled = node0.geom_info["vertex"] @ S0.T
    # Scale down the other wall to remove the width of the dominant wall
    unit_vec_1 = vec_1[1]/scalars_1[1]
    S1 = np.eye(3) + ((scalars_0[1] + scalars_1[0])/scalars_1[1]) * np.outer(unit_vec_1, unit_vec_1)
    V1_scaled = node1.geom_info["vertex"] @ S1.T
    return V0_scaled, V1_scaled
def make_corner_type_2(node0, node1):
    """
    Creating a 45 degree corner. 
    We know the overlapping point is always in the outer line.
    """
     
    dominant_wall = return_dominant_wall(node0, node1)
    intersections = GP.np_intersect_rows(node0.geom_info["vertex"], node1.geom_info["vertex"], return_type = "index")
    
    

    # base_curve_0 = GP.get_base_curve(node0)
    # base_curve_1 = GP.get_base_curve(node1)
    # vec_0 = GP.decompose_2D_from_base(base_curve_0)
    # vec_1 = GP.decompose_2D_from_base(base_curve_1)
    # print(base_curve_0)
    # print(base_curve_1)
    return