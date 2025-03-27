import ifcopenshell
import numpy as np
from pathlib import Path
from utils import  Graph, get_geom_info
from traversal import get_adjacent
from geometry_processing import angle_between, boolean_3D
import trimesh
import collision
import display
import math
import export as E

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

    # Get all connected same type (wall and slab)
    # ====================================================================
    result_W = graph.merge_by_type("IfcWall")
    result_S = graph.merge_by_type("IfcSlab")
    result_R = graph.merge_by_type("IfcRoof")
    print("Wall",result_W)
    print("Slabs",result_S)
    print("Roof",result_R)

    # Boolean Operations and export to ifc for viewing
    # ====================================================================
    new_model = E.copy_project_structure(model)
    result = result_W | result_S | result_R
    bool_results = []
    for key, values in result.items():
        nodes = [graph.node_dict[guid] for guid in values]
        bool_result = boolean_3D(nodes, operation="union", return_type = "vf_list")
        bool_results.append(bool_result)
        E.modify_element_to_model(model, new_model, key, vertices=bool_result[0], faces= bool_result[1])

    new_model.write("data/ifc/meow1.ifc")
    # Adding other parts that are not booleaned
    # ============================
    booled = [item for sublist in result.values() for item in sublist ]
    for key,value in graph.node_dict.items():
        if key not in booled:
            print(value.psets)
            # Use the original geometry and rebuild
            E.modify_element_to_model(model, new_model, key, value.geom_info["vertex"], value.geom_info["face"])
    new_model.write("data/ifc/meow2.ifc")


    # Displaying particular boolean/mesh/points in custom viewer
    # ====================================================================
    # display.show(
    #     display.mesh(bool_results, obj_type = "vf_list")
    #)

    # display.show([
    #     # display.mesh([node], show_edges = True),
    #     display.points(temp[0]),
    #     display.vector(temp[1], origin = temp[0][0])
    #               ])
    # bool_result = [boolean_3D(results, operation="union")]
    # showMesh(bool_result)


if __name__ == "__main__":
    main()