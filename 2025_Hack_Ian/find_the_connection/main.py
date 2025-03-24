import ifcopenshell
import numpy as np
import math
from pathlib import Path
from utils import  Graph, get_geom_info_for_check
from traversal import get_adjacent
from export import create_ifc_for_partial_model
from geometry_processing import decompose_2D_from_base, angle_between, boolean_3D, get_base_curve
import trimesh
import collision
import display

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

    # Get all connected same type (wall and slab) 
    # ====================================================================
    # result = graph.merge_adjacent(guid2)
    # results = [graph.node_dict[guid] for guid in result]
    # bool_result = [boolean_3D(results, operation="union")]
    # showMesh(bool_result)

    #  Get all connected same type (inclinde geom / roof) using PCA / Convex Hull Best face
    # ====================================================================
    nodeR0 = graph.node_dict["1QmrSv$7f8vB34GVkkI57J"]
    nodeR1 = graph.node_dict["0TAmI$AOf2HOFYvSNZEV2u"]
    nodeR2 = graph.node_dict["0zlLHiur1ElR$u0pjr99AU"]
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
    result_R = graph.merge_by_type("IfcRoof")
    print("Wall",result_W)
    # print("Slab",result_S)
    # print("Roof",result_R)

    node0 = graph.node_dict["2oMNvrrQvE1uhdDRYExAXf"]
    node1 = graph.node_dict["31_nGQTvv9ee_NlwTpsOH5"]
    info0 = get_geom_info_for_check(node0)
    info1 = get_geom_info_for_check(node1)
    v0 = info0["vectors"]
    v1 = info1["vectors"]
    angles = angle_between(v0[1], v1[1])
    print(v0[1])
    print(v1[1])
    print(angles * 180/math.pi)
    # angles = angle_between(v0, v1)
    # print(v0@v1.T)
    # mask  = (np.abs(angles) < 1e-4) | (np.abs(angles - math.pi) < 1e-4)
    # print(angles * 180/math.pi)
    # print(mask)
    # print(result_W["0DPk3As8fAPwVPbv4Ds3ps"])
    # Q = model.by_guid("2e$6kGnQX60QRbpq8u7ZAq")
    # nodeQ = graph.node_dict["2e$6kGnQX60QRbpq8u7ZAq"]
    # print(nodeQ.geom_info)

    # Displaying mesh, points or vectors
    # ====================================================================
    # result = result_R
    # node = graph.node_dict[result.keys[0]]
    # results = result[result.values[0]]
    # print(node)
    # print(results)
    # display.show([
    #     display.mesh([nodeR0], edge_only= True),
    #     display.points(temp[0]),
    #     display.vector(temp[1], origin = temp[0][0], length = 5)
    #               ])

    # Exporting the model after rewriting the geometry to ifc
    # ====================================================================
    # export = []
    # for values in result_W.values():
    #     export.extend(values)
    # create_ifc_for_partial_model(export, model, file_path = export_path)

if __name__ == "__main__":
    main()