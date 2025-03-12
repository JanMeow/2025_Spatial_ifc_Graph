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
def create_ifc_for_partial_model(entity, model, schema = "IFC4", write_file = True, file_path = "new_model.ifc", save_props = True):
  # Create_basic_skeleton
  new_model, storey = create_basic_project_strcuture(entity, schema = "IFC4", relationship = "IfcRelAggregates")
  partial_grapth = model.traverse(entity)
  # Copying the entities into an object and linking it to the storey level
  for i,node in enumerate(partial_grapth):
    copied_entity = new_model.add(node)
    if i == 0:
      root_node = copied_entity
    # Traverse does not contain the custom property, so we need to get those also
    if save_props and hasattr(node, "IsDefinedBy"):
      props = node.IsDefinedBy
      for prop in props:
        new_model.add(prop)
  # Linking to the storey level
  new_model.create_entity(
    "IfcRelContainedInSpatialStructure",
    GlobalId=ifcopenshell.guid.new(),
    RelatingStructure=storey,
    RelatedElements=[root_node],
)
  if write_file:
    new_model.write(file_path)

  return new_model