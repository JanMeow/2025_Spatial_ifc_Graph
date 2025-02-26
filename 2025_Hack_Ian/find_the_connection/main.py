from pathlib import Path
import ifcopenshell
from utils import  Graph, Node
from intersection_test import  get_adjacent, get_direct_connection, loop_detecton


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
    column = model.by_type("IfcColumn")[0]

    # Create a graph
    graph = Graph.create(root)
    # Establish BVH Tree for the nodes 
    graph.build_bvh()

    node1 = graph.node_dict[guid1]
    node2 = graph.node_dict[guid2]
    queries = graph.bvh_query(node1.geom_info["bbox"])
    adjs = get_adjacent(model, proxy1)
    print(queries)
    print(adjs)




    # Build the graph based on relationship
    # for node in graph.node_dict.values():
    #     if node.geom_info["bbox"] == None:
    #         print(node.geom_info)
    #         print("sad", node.geom_type)
        # entity = model.by_guid(key)
        # adj_nodes_guid = get_adjacent(model, entity)
        # node.near = [graph.node_dict[guid] for guid in adj_nodes_guid]




    # Show the direct connection
    # print(get_direct_connection(proxy1, graph)[0])

    # print("start loop detection")
    # node = graph.node_dict["3hP3TktpfEHuFubiINX0a$"]
    # print(loop_detecton(node, max_depth=3))
    # print("done")





if __name__ == "__main__":
    main()