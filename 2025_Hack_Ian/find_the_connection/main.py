import ifcopenshell
import numpy as np
from pathlib import Path
from utils import  Graph, get_geom_info_for_check
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
    key = list(result_W.keys())[0]
    node = graph.node_dict[key]
    T_matrix = node.geom_info["T_matrix"]
    results = [graph.node_dict[guid] for guid in result_W[key]]
    bool_result = [boolean_3D(results, operation="union", return_type= "vf_list")]
    # print(bool_result[0][0])
    local_coor = get_local_coors(T_matrix, bool_result[0][0])
    print(get_local_coors(T_matrix, bool_result[0][0]))
    coords_tuple = tuple(tuple(row) for row in local_coor)
    print(coords_tuple)
    # display.show(display.mesh(bool_result, obj_type = "trimesh"))

    # Change the geometry of the ifc element from the node
    # ====================================================================
    # id = "1QmrSv$7f8vB34GVkkI57J"
    element = model.by_guid(key)
    # print(node_e.geom_info)
    ele_shape = element.Representation
    shape_rep = ele_shape.Representations [0]  # the IfcShapeRepresentation
    tess_item = shape_rep.Items[0]  # e.g. IfcTriangulatedFaceSet or IfcPolygonalFaceSet
    # print(node_e.geom_info["vertex"])
    # print(node_e.get_local_coors())    

    def rewrite_ifc_geometry(model, guid, new_vf_list = None):
        node = graph.node_dict[guid]
        element = model.by_guid(guid)
        ele_shape = element.Representation
        shape_rep = ele_shape.Representations[0]
        tess_item = shape_rep.Items[0]

        if tess_item.is_a("IfcTriangulatedFaceSet") or tess_item.is_a("IfcPolygonalFaceSet"):
            old_v = tess_item.Coordinates.CoordList
            new_v = ""
        print(old_v)
        placement = element.ObjectPlacement
        if placement and placement.is_a("IfcLocalPlacement"):
            print(placement)
            axis_placement = placement.RelativePlacement
        if axis_placement.is_a("IfcAxis2Placement3D"):
            # All these information are in the T-matrix hehe
            origin = axis_placement.Location           # IfcCartesianPoint
            axis   = axis_placement.Axis              # IfcDirection (optional)
            refdir = axis_placement.RefDirection       # IfcDirection (optional)
            # print("Origin:", origin.Coordinates)
            # print("Axis:", axis)
            # print("Refdir:", refdir)
        return
    # rewrite_ifc_geometry(model, guid = key)

    # Displaying mesh, points or vectors
    # ====================================================================
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
    E.export(result_W[key], model, file_path= export_path)
    # model_new.write("data/ifc/hahaha.ifc")


if __name__ == "__main__":
    main()