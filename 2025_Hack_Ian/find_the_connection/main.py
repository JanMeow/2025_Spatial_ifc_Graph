from pathlib import Path
import ifcopenshell
from utils import bfs_traverse, get_geometry_info, write_to_node, create_graph
from intersection_test import get_planes, get_adjacent, get_direct_connection, loop_detecton


ifc_folder = Path("data")/"ifc"
ifc_folder.mkdir(parents=True, exist_ok=True)


ifc_path = ifc_folder/"example1.ifc"


def main():
    # Read the IFC file:
    model = ifcopenshell.open(ifc_path)
    print(model.schema)

    root = model.by_type("IfcProject")[0]
    proxy1 = model.by_guid("3hP3TktpfEHuFubiINX0a$")
    proxy2 = model.by_guid("3o14as6$P1GQOeedYgIq1J")

    # Get geometric information from 
    # print(get_geometry_info(proxy1, get_global=True))

    # Create a graph
    graph = create_graph(root)


    # test for intersectionrs
    # result = get_intersection(proxy1, proxy2)
    # print(result)

    # Get triangulated equation
    # get_planes(proxy1, get_global=True)
    adj_nodes = get_adjacent(model, proxy1)
    print(adj_nodes)


    # Build the graph based on relationship
    for key, node in graph.node_dict.items():
        entity = model.by_guid(key)
        adj_nodes_guid = get_adjacent(model, entity)
        node.near = [graph.node_dict[guid] for guid in adj_nodes_guid]




    # Show the direct connection
    # print(get_direct_connection(proxy1, graph)[0])

    print("start loop detection")
    node = graph.node_dict["3hP3TktpfEHuFubiINX0a$"]
    print(loop_detecton(node, max_depth=3))
    print("done")





if __name__ == "__main__":
    main()