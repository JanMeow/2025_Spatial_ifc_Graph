import ifcopenshell
import numpy as np
from pathlib import Path
from utils import  Graph, get_triangulated_planes
from traversal import get_adjacent
from collision import gjk
from export import create_ifc_for_partial_model
from geometry_processing import decompose_2D, angle_between, boolean_3D, showMesh
from collections import Counter
import trimesh



# ====================================================================
ifc_folder = Path("data")/"ifc"
ifc_folder.mkdir(parents=True, exist_ok=True)
ifc_path = ifc_folder/"sample_for_test.ifc"
export_path = "data/ifc/new_model.ifc"

def main():
    # Read the IFC file:
    model = ifcopenshell.open(ifc_path)
    print(model.schema)

    root = model.by_type("IfcProject")[0]
    guid1 = "0js3D2vQP9PeLECr8TXDwW"
    proxy1 = model.by_guid(guid1)

    # # Create a graph
    graph = Graph.create(root)
    # Establish BVH Tree for the nodes 
    graph.build_bvh()

    node1 = graph.node_dict[guid1]
    queries = graph.bvh_query(node1.geom_info["bbox"])
    print(queries)



    # Build the graph based on relationship
    for node in graph.node_dict.values():
        if node.geom_info != None:
            node.near = [graph.node_dict[guid] for guid in graph.bvh_query(node.geom_info["bbox"])
                         if guid != node.guid]

    # Show the direct connection
    # print(graph.get_connections(guid1))

    # Detecting Corner around using loop detection
    # print(graph.loop_detection(guid1, max_depth=3))

    # Test Narrow Phase Collision Detection
    # gjk_test = graph.gjk_query(guid1, guid2)

    # Get all connected same type => Wall merging
    result = graph.merge_adjacent(guid1)
    print(result)
    result = [graph.node_dict[guid] for guid in result]
    queries = [(graph.node_dict[guid].geom_info["vertex"], graph.node_dict[guid].geom_info["faceVertexIndices"]) for guid in queries]
    bool_result = [boolean_3D(result[0], result[1], type="union")]
    showMesh(bool_result)
    print("hahahaha")

    # create_ifc_for_partial_model(proxy1, model, file_path = export_path)


if __name__ == "__main__":
    main()