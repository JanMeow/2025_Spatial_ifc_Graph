import ifcopenshell
from pathlib import Path
from utils import  Graph, Node
from traversal import get_adjacent


ifc_folder = Path("data")/"ifc"
ifc_folder.mkdir(parents=True, exist_ok=True)
ifc_path = ifc_folder/"example1.ifc"


def main():
    # Read the IFC file:
    model = ifcopenshell.open(ifc_path)
    print(model.schema)

    root = model.by_type("IfcProject")[0]
    guid1 = "3hP3TktpfEHuFubiINX0a$"
    guid2 = "3o14as6$P1GQOeedYgIq1J"
    proxy1 = model.by_guid(guid1)
    proxy2 = model.by_guid(guid2)


    # # Create a graph
    graph = Graph.create(root)
    # Establish BVH Tree for the nodes 
    graph.build_bvh()

    node1 = graph.node_dict[guid1]
    node2 = graph.node_dict[guid2]
    queries = graph.bvh_query(node1.geom_info["bbox"])
    adjs = get_adjacent(model, proxy1)


    # Build the graph based on relationship
    for node in graph.node_dict.values():
        if node.geom_info != None:
            node.near = [graph.node_dict[guid] for guid in graph.bvh_query(node.geom_info["bbox"])
                         if guid != node.guid]


    # Show the direct connection
    # print(graph.get_connections(guid2))

    # Detecting Corner around using loop detection
    # print(graph.loop_detection(guid1, max_depth=3))

    # Test Narrow Phase Collision Detection
    print(node1.geom_info)



if __name__ == "__main__":
    main()