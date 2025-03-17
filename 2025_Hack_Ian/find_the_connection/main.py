import ifcopenshell
import numpy as np
from pathlib import Path
from utils import  Graph, get_triangulated_planes
from traversal import get_adjacent
from export import create_ifc_for_partial_model
from geometry_processing import decompose_2D, angle_between, boolean_3D, showMesh
import trimesh
import collision

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
    guid2  = "1ExlF2Qnv1QA32hRKgFhNX"
    proxy1 = model.by_guid(guid1)

    # # Create a graph
    graph = Graph.create(root)
    # Establish BVH Tree for the nodes 
    graph.build_bvh()

    node1 = graph.node_dict[guid1]
    queries = graph.bvh_query(node1.geom_info["bbox"])

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

    # Get all connected same type
    result = graph.merge_adjacent(guid1)
    # print(result)

    # Dealing with roof geometry (inclinde geom)
    nodeR = graph.node_dict["3XDvnQJPj2B9J$8W1k1bdZ"]
    # obb = trimesh.bounds.oriented_bounds(nodeR.geom_info["vertex"])
    # print(obb)
    result = [graph.node_dict[guid] for guid in result]
    bool_result = [boolean_3D(result[0], result[1], type="union")]

    f_idx = nodeR.geom_info["faceVertexIndices"]
    v = nodeR.geom_info["vertex"]
    faces = v[f_idx]
    

    temp = np.array(collision.create_OOBB(faces, v), dtype=np.float32)
    temp_idx = np.array([2,1,0], dtype=np.uint32).reshape(-1,3)
    print(bool_result)

    display = [(temp, temp_idx)]
    print(display)

    # showMesh(bool_result)
    

    def show_points_as_spheres(points, radius=0.05, geom_info = nodeR.geom_info):

        scene = trimesh.Scene()
        mesh_R = trimesh.Trimesh(vertices =geom_info["vertex"], faces =geom_info["faceVertexIndices"])

        # Create a sphere mesh at each point
        for point in points:
            sphere = trimesh.creation.icosphere(subdivisions=3, radius=radius)  # High-quality sphere
            sphere.apply_translation(point)  # Move sphere to correct position
            scene.add_geometry(sphere)
        # Set camera to focus on points
        edges = mesh_R.edges_unique
        edge_vertices = mesh_R.vertices[edges]
        for edge in edge_vertices:
            line = trimesh.load_path(edge)  # Creates a line segment
            scene.add_geometry(line)
        scene.set_camera(distance=10, center=np.mean(points, axis=0))
        scene.show()

    show_points_as_spheres(temp)

    # create_ifc_for_partial_model(proxy1, model, file_path = export_path)


if __name__ == "__main__":
    main()