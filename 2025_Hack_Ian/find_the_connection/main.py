from pathlib import Path
import ifcopenshell
from utils import  Graph
from intersection_test import  get_adjacent, get_direct_connection, loop_detecton


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



    # Create a graph
    graph = Graph.create(root)
    overall = graph.get_bbox()
    print(overall)

    # test for intersectionrs
    # result = get_intersection(proxy1, proxy2)
    # print(result)



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