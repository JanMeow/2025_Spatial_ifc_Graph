import ifcopenshell
import numpy as np
from pathlib import Path
from utils import  Graph, get_triangulated_planes, np_intersect_rows
from traversal import get_adjacent
from export import create_ifc_for_partial_model
from geometry_processing import decompose_2D, angle_between, boolean_3D, get_base_curve
import trimesh
import collision
import display
import math

# ====================================================================
ifc_folder = Path("data")/"ifc"
ifc_folder.mkdir(parents=True, exist_ok=True)
ifc_path = ifc_folder/"test2.ifc"
export_path = "data/ifc/new_model.ifc"

def main():
    # Read the IFC file:
    # ====================================================================
    model = ifcopenshell.open(ifc_path)
    root = model.by_type("IfcProject")[0]

    # # Create a graph and establish BVH Tree
    # ====================================================================
    graph = Graph.create(root)
    graph.build_bvh()

    # Build the graph based on relationship
    # ====================================================================
    for node in graph.node_dict.values():
        if node.geom_info != None:
            node.near = [graph.node_dict[guid] for guid in graph.bvh_query(node.geom_info["bbox"])
                         if guid != node.guid]

    # Show the direct connection
    # ====================================================================
    # print(graph.get_connections(guid1))

    # Detecting Corner around using loop detection
    # ====================================================================
    # print(graph.loop_detection(guid1, max_depth=3))

    # Test Narrow Phase Collision Detection
    # ====================================================================
    # gjk_test = graph.gjk_query(guid1, guid2)

    # Get all connected same type (wall and slab)
    # ====================================================================
    walls = [i.GlobalId for i in model.by_type("IfcWall")]
    slabs = [i.GlobalId for i in model.by_type("IfcSlab")]
    print("Walls")
    print(graph.merge_type(model, "IfcWall"))
    # for guid in walls:
    #     result  = graph.merge_adjacent(guid)
    #     print(result)
    print("Slabs")
    for guid in slabs:
        result  = graph.merge_adjacent(guid)
        print(result)






    # result = graph.merge_adjacent(guid2)
    # results = [graph.node_dict[guid] for guid in result]
    # bool_result = [boolean_3D(results, operation="union")]
    # showMesh(bool_result)

    #  Get all connected same type (inclinde geom / roof) using PCA / Convex Hull Best face
    # ====================================================================
    roof = [i.GlobalId for i in model.by_type("IfcRoof")]

    # PCA Decomposition
    # ============================
    # temp = collision.create_OOBB(nodeR0, "PCA")
    # print(temp0[2][1]-temp0[2][0])
    # print(temp1[2][1]-temp1[2][0]) 
    # print(temp2[2][1]-temp2[2][0])
    # print(temp1[1])
    # print(temp2[1])
    # print(collision.check_pca_similarity(temp0[1], temp1[1], atol = 1e-3, method = "Hungarian"))
    # print(collision.check_pca_similarity(temp0[1], temp1[1], atol = 1e-3, method = "Gaussian"))   
    # Convex Hull Decomposition
    # ============================
    # temp = collision.create_OOBB(nodeR0, "ConvexHull")
    # print(temp[1])

    # Displaying mesh, points or vectors
    # ====================================================================
    # display.show([
    #     display.mesh([nodeR0], show_edges = True),
    #     display.points(temp[0]),
    #     display.vector(temp[1], origin = temp[0][0])
    #               ])

    # Exporting the model after rewriting the geometry to ifc
    # ====================================================================
    # create_ifc_for_partial_model(proxy1, model, file_path = export_path)

if __name__ == "__main__":
    main()