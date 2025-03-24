import ifcopenshell
# ====================================================================
#  Functons for exporting partial IFC model
# ====================================================================
def create_basic_project_strcuture(entity, schema = "IFC4", relationship = "IfcRelAggregates"):

  spatial_hierachy = ["IfcProject","IfcSite", "IfcBuilding", "IfcBuildingStorey"]
  # Instantiate a new model
  new_model = ifcopenshell.file(schema = schema)
  # Get the spatial level of the entity you want to create
  spatial_level = entity.is_a()
  # Create_basic_skeleton
  def create():
    prev = None
    for item in spatial_hierachy:
      if item == "IfcProject":
        new_spatial_layer = new_model.create_entity(item, GlobalId=ifcopenshell.guid.new(), Name= "Sample" + item)
        context = new_model.create_entity("IfcGeometricRepresentationContext", ContextType="Model", ContextIdentifier="Building Model")
        new_spatial_layer.RepresentationContexts = [context]
      else:
        new_spatial_layer = new_model.create_entity(item, GlobalId=ifcopenshell.guid.new(), Name= "Sample" + item)
      if prev != None:
        new_relationship = new_model.create_entity(relationship, GlobalId=ifcopenshell.guid.new(), RelatingObject=prev, RelatedObjects=[new_spatial_layer])
      prev = new_spatial_layer
    return new_model, prev
  return create()
def set_property (model, entity, property_name,property_value, property_type = "IFCPROPERTYSINGLEVALUE"):
  #Here propety value has to be of an ifc type, for example IFCREAL(304.00) or IFC Integer
  # For type safty in the future, might need to add conversion
  NominalValue =real_value = model.create_entity("IfcReal", property_value)

  # Create the Value object and the property object that links the two
  new_property = model.create_entity(property_type, Name = property_name, NominalValue = NominalValue )
  property_set = model.create_entity("IfcPropertySet", GlobalId=ifcopenshell.guid.new(), Name=f"{property_name}_set", HasProperties = [new_property])
  # Create Relational Instance
  model.create_entity(
        "IfcRelDefinesByProperties",
        GlobalId=f"NEW_REL_{ifcopenshell.guid.new()}",
        RelatingPropertyDefinition=property_set,
        RelatedObjects=[entity]
    )
  return entity
def create_ifc_for_partial_model(guids, model, schema="IFC4", write_file=True, file_path="new_model.ifc", save_props=True):
    """
    Export a partial IFC model that includes multiple elements identified by their GUIDs.

    :param guids: List of IFC element GlobalIds to export.
    :param model: The source ifcopenshell model.
    :param schema: IFC schema (default: "IFC4").
    :param write_file: Whether to write the result to a file.
    :param file_path: Output path for the IFC file.
    :param save_props: Whether to preserve property sets.
    :return: New partial ifcopenshell model.
    """
    # Step 1: Create new basic IFC project
    new_model, storey = create_basic_project_strcuture(model.by_guid(guids[0]), schema=schema, relationship="IfcRelAggregates")

    all_nodes = set()
    root_nodes = []

    # Step 2: Traverse and collect all connected entities
    for guid in guids:
        entity = model.by_guid(guid)
        if not entity:
            print(f"Warning: Entity with GUID {guid} not found.")
            continue

        partial_graph = model.traverse(entity)
        root_nodes.append(entity)
        all_nodes.update(partial_graph)
    guid_to_copy = {}
    # Step 3: Copy elements into the new model
    for node in all_nodes:
        copied_entity = new_model.add(node)
        if hasattr(node, "GlobalId") == False:
            continue
        guid_to_copy[node.GlobalId] = copied_entity
        # Copy properties if requested
        if save_props and hasattr(node, "IsDefinedBy"):
            for prop in node.IsDefinedBy:
                new_model.add(prop)
    # Step 4: Link copied root nodes to storey
    new_model.create_entity(
        "IfcRelContainedInSpatialStructure",
        GlobalId=ifcopenshell.guid.new(),
        RelatingStructure=storey,
        RelatedElements=[guid_to_copy[root.GlobalId] for root in root_nodes if root.GlobalId in guid_to_copy]
    )
    # Step 5: Write the model to disk
    if write_file:
        new_model.write(file_path)
    return new_model