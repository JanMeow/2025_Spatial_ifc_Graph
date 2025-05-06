import ifcopenshell
import numpy as np
from pathlib import Path
from utils import  Graph, merge_test, np_intersect_rows
from traversal import get_adjacent, bfs_traverse
import trimesh
import collision
import display
import export as E
import geometry_processing as GP
import cornering as C
# ===================================================================================
# Global Variables for import and export file paths
# ===================================================================================
ifc_folder = Path("data")/"ifc"
ifc_folder.mkdir(parents=True, exist_ok=True)
ifc_path = ifc_folder/"test1.ifc"
export_path = "data/ifc/new_model.ifc"
# ===================================================================================
# ===================================================================================
# ====================================================================
# Main function to run the script
# ====================================================================
def main():
    # Read the IFC file:
    # ====================================================================
    model = ifcopenshell.open(ifc_path)
    root = model.by_type("IfcProject")[0]

    # # Create a graph and establish BVH Tree
    # ====================================================================
    graph = Graph.create(root)
    graph.build_bvh()
    # node = graph[guid]
    # queries = graph.bvh_query(node.geom_info["bbox"])

    # Build the graph based on relationship
    # ====================================================================
    for node in graph.node_dict.values():
        if node.geom_info != None:
            node.near = [graph[guid] for guid in graph.bvh_query(node.geom_info["bbox"])
                         if guid != node.guid]
    # The original input ifc roof were not typed so i have to do it manually.
    roof_id = ["28aBLRPE1BG8SIr2KuT2kw","3XDvnQJPj2B9J$8W1k1bdZ", "3Zr2lZTZj0GhCS2xwxq5AA", "3Zr2lZTZj0GhCS2xwxq5AA",
               "0_rR1BdgX1VwLmdcGWmD2O", "1K$8Ku4NPFcAJ9X46IE_rz", "0zlLHiur1ElR$u0pjr99AU", "0TAmI$AOf2HOFYvSNZEV2u", 
               "1QmrSv$7f8vB34GVkkI57J", "38etAjtY94yR9Iz7PW6muJ", "3vCHKIfl5D98aKKOrI_mXU", "38etAjtY94yR9Iz7PW6muJ",
               "2t5Dc_P6LAQxsNJlWPfvpN", "0kg6FaO3975AZ4ew2GsBwm", "00n4wBngLESh3sJgGPM8tl", "3U_YbDPkP8wh$il6GPzfG6",
               "3g_LwPgxPAxRWRbwjTaX27", "19F6LEtSbAVBR1XKPuuhuV","0s2avnVezEQxP3GDgRf3dd", "2FQHPJ30nEVPcqIUba8A5n"]
    for id in roof_id:
        node = graph[id]
        node.geom_type = "IfcRoof"

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
    nodeR0 = graph[r0]
    nodeR1 = graph[r1]
    nodeR2 = graph[r2]
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
    # result_W = graph.merge_by_type("IfcWall")
    # result_S = graph.merge_by_type("IfcSlab")

    # result_R = graph.merge_by_type("IfcRoof")
 
    # Boolean Operation
    # ====================================================================
    # plain_model, storey = E.create_project_structure()
    # result = result_W | result_S | result_R
    # bool_results = []
    # for key, values in result.items():
    #     nodes = [graph.node_dict[guid] for guid in values]
    #     bool_result = GP.boolean_3D(nodes, operation="union", return_type = "vf_list")
    #     bool_results.append(bool_result)
    #     E.create_element_in_model(plain_model, graph, key, vertices=bool_result[0], faces= bool_result[1], shape = "PolygonalFaceSet")
    # plain_model.write("data/ifc/p_meow1.ifc")

    # # Adding other parts that are not booleaned
    # # ============================
    # booled = [item for sublist in result.values() for item in sublist ]

    # for key,value in graph.node_dict.items():
    #     if key not in booled:
    #         E.create_element_in_model( plain_model, graph, key, value.geom_info["vertex"], value.geom_info["face"], shape = "PolygonalFaceSet")
    # plain_model.write("data/ifc/P_meow2.ifc")
   

    # ====================================================================
    # TESTING EXPORT  Currently there are problem in copying the project structure for some files
    # ====================================================================
    # new_model = E.copy_project_structure(model, max_depth=1)
    # new_model2, storey = E.create_project_structure()
    # new_model.write("data/ifc/meow0.ifc")

    """
    Problem1
    fixing why the export does not work when it reaches building level
    """
    # project = model.by_type("IfcProject")[0]
    # new_project = model.by_type("IfcProject")[0]
    # building = model.by_type("IfcBuilding")[0]
    # print(project.OwnerHistory)
    # print(new_project.OwnerHistory)
    # print(building.get_info())

    """
    Problem2
    some object are not directly stored in the space
    """
    #Problem2, some object are not directly stored in the space
    # print(E.get_container_rel(model,"3XDvnQJPj2B9J$8W1k1bdZ"))
    # print(graph["3XDvnQJPj2B9J$8W1k1bdZ"].geom_type)
    # assigns = [rel for rel in new_model.by_type("IfcRelAssignsToGroup")
    #        if rel.RelatingGroup and rel.RelatingGroup.GlobalId == roof.GlobalId]
    # print(assigns)


    # roof_element = model.by_guid("3XDvnQJPj2B9J$8W1k1bdZ")
    # print(E.get_container_rel(model,"3XDvnQJPj2B9J$8W1k1bdZ"))
    # print(ifcopenshell.util.element.get_container(roof_element))
    # # _copy = ifcopenshell.api.root.copy_class(roof_element)
    # # print(_copy.GlobalId)
    # print(graph.node_dict["3XDvnQJPj2B9J$8W1k1bdZ"].geom_type)
    # for key, values in result.items():
    #     nodes = [graph[guid] for guid in values]
    #     bool_result = boolean_3D(nodes, operation="union", return_type = "vf_list")
    #     bool_results.append(bool_result)
    #     E.modify_element_to_model(model, new_model, graph, key, vertices=bool_result[0], faces= bool_result[1])
    # new_model.write("data/ifc/meow1.ifc")

    # Displaying mesh, points, boolean or vectors
    # ====================================================================
    # display.show(display.mesh(bool_result, obj_type = "trimesh"))

    # node = graph[result.keys[0]]
    # results = result[result.values[0]]
    # print(node)
    # print(results)
    # display.show([
    #     display.mesh([nodeR0], edge_only= True),
    #     display.points(temp[0]),
    #     display.vector(temp[1], origin = temp[0][0], length = 1)
    #               ])

    #Cornering
    # ====================================================================
    corners = C.find_wall_corners(graph)
    for i, (A,B) in enumerate(zip(corners["A"], corners["B"])):
        if i >1:
            break
        nodeA = graph[A]
        nodeB = graph[B]
        print("Before")
        print(nodeA.geom_info["vertex"])
        A_scaled, B_scaled = C.scale_wall_to(nodeA, nodeB)
        print("After")
        print(A_scaled)
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