import ifcopenshell
import numpy as np
from pathlib import Path
from utils import  Graph, get_geom_info
from traversal import get_adjacent
from geometry_processing import decompose_2D_from_base, angle_between, boolean_3D, get_local_coors
import trimesh
import collision
import display
import export as E

# ====================================================================
ifc_folder = Path("data")/"ifc"
ifc_folder.mkdir(parents=True, exist_ok=True)
ifc_path = ifc_folder/"test1.ifc"
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
    # node = graph.node_dict[guid]
    # queries = graph.bvh_query(node.geom_info["bbox"])

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

    #  Get all connected same type (inclinde geom / roof) using PCA / Convex Hull Best face
    # ====================================================================
    r0 = "1QmrSv$7f8vB34GVkkI57J"
    r1 = "0TAmI$AOf2HOFYvSNZEV2u"
    r2 = "0zlLHiur1ElR$u0pjr99AU"
    nodeR0 = graph.node_dict[r0]
    nodeR1 = graph.node_dict[r1]
    nodeR2 = graph.node_dict[r2]
    # PCA Decomposition
    # ============================
    # temp0 = collision.create_OOBB(nodeR0, "PCA")
    # temp1 = collision.create_OOBB(nodeR1, "PCA")
    # print(temp0[2][1]-temp0[2][0])
    # print(temp1[2][1]-temp1[2][0]) 
    # print(temp1[1])
    # Similarity Check using Hungarian / Gaussian method
    # ============================
    # print(collision.check_pca_similarity(temp0[1], temp1[1], atol = 1e-6, method = "Hungarian"))
    # print(collision.check_pca_similarity(temp0[1], temp1[1], atol = 1e-3, method = "Gaussian")) 
    # Convex Hull Decomposition
    # ============================
    # temp = collision.create_OOBB(nodeR0, "ConvexHull")
    # print(temp[1])

    # Get all connected same type (wall and slab)
    # Roof elements are tested against their PCA/ Convex Hull similarity 
    # ====================================================================
    result_W = graph.merge_by_type("IfcWall")
    result_S = graph.merge_by_type("IfcSlab")
    # This does not work on test1.ifc because no elements are typed ifcroof
    result_R = graph.merge_by_type("IfcRoof")
    # print("Wall",result_W)
    # print("Slab",result_S)
    # print("Roof",result_R)    
    # print(nodeR0.geom_info)


    # Boolean Operation
    # ====================================================================
    new_model = E.copy_project_structure(model)
    result = result_W | result_S | result_R
    bool_results = []
    for key, values in result.items():
        nodes = [graph.node_dict[guid] for guid in values]
        bool_result = boolean_3D(nodes, operation="union", return_type = "vf_list")
        bool_results.append(bool_result)
        # E.modify_element_to_model(model, new_model, key, vertices=bool_result[0], faces= bool_result[1])
  
    # Displaying mesh, points, boolean or vectors
    # ====================================================================
    # display.show(display.mesh(bool_result, obj_type = "trimesh"))

    # node = graph.node_dict[result.keys[0]]
    # results = result[result.values[0]]
    # print(node)
    # print(results)
    # display.show([
    #     display.mesh([nodeR0], edge_only= True),
    #     display.points(temp[0]),
    #     display.vector(temp[1], origin = temp[0][0], length = 1)
    #               ])

    # Exporting the model after rewriting the geometry to ifc
    # ====================================================================
    # export = []
    # for values in result_W.values():
    #     export.extend(values)
    # E.export(export, model, file_path = export_path)
    # model_new = E.create_basic_structure(ref= model)[0]
    # element = E.create_ifc_element_from_node(model_new, nodeR0)
    # E.export([key], model, file_path= export_path)
    # model_new.write("data/ifc/hahaha.ifc")


if __name__ == "__main__":
    main()