import time
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util
import ifcopenshell.util.element as element
# ====================================================================
#  Functons for exporting partial IFC model
# ====================================================================
def create_owner_history(model):
  user = model.create_entity(
          "IfcPerson",
          Identification="UserID",
          FamilyName="Doe",
          GivenName="John",
      )
  organization = model.create_entity(
      "IfcOrganization",
      Identification="BFH",
      Name="BFH_Dokwood"
  )
  person_org = model.create_entity(
          "IfcPersonAndOrganization",
          ThePerson=user,
          TheOrganization=organization
      )
  application = model.create_entity(
            "IfcApplication",
            ApplicationDeveloper=organization,  # IfcOrganization
            Version="1.0",
            ApplicationFullName="Dokwood_Application",
            ApplicationIdentifier="Dokwood_0.0.0"
        )
  owner_history = model.create_entity(
            "IfcOwnerHistory",
            OwningUser=person_org,
            OwningApplication=application,
            State=None,
            ChangeAction=None,
            LastModifiedDate=None,
            LastModifyingUser=None,
            LastModifyingApplication=None,
            CreationDate=int(time.time())
        )
  return owner_history
def wrap_ifc_value(model, val):
  """
  Convert a Python value (int, float, str) into an IFC4-compliant entity,
  e.g. IfcInteger, IfcReal, IfcLabel, IfcText, etc.
  """
  if isinstance(val, float):
      # IFC expects a select type like IfcReal
      return model.create_entity("IfcReal", val)
  elif isinstance(val, int):
      # IFC expects IfcInteger
      return model.create_entity("IfcInteger", val)
  elif isinstance(val, str):
      # Could use IfcLabel (short text) or IfcText (long text). 
      # If not sure, IfcLabel is most common.
      return model.create_entity("IfcLabel", val)
  else:
      # For bool or other types, adapt to your needs.
      # We can just treat it as text, or skip.
      return model.create_entity("IfcLabel", str(val))
def check_for_file_references(entity, visited=None):
    """Recursively walk all attributes to see if anything references a file object."""
    if visited is None:
        visited = set()
    if entity in visited:
        return
    visited.add(entity)

    info = entity.get_info()
    for attr_name, attr_val in info.items():
        if isinstance(attr_val, ifcopenshell.file):
            print(f"WARNING: Found a direct reference to file in '{entity}' at attribute '{attr_name}'")
        elif isinstance(attr_val, ifcopenshell.entity_instance):
            check_for_file_references(attr_val, visited)
        elif isinstance(attr_val, list):
            for v in attr_val:
                if isinstance(v, ifcopenshell.entity_instance):
                    check_for_file_references(v, visited)
# ====================================================================
def create_basic_structure(ref = None, schema = "IFC4"):
    new_model = ifcopenshell.file(schema = schema)
    spatial_hierachy = ["IfcProject","IfcSite", "IfcBuilding", "IfcBuildingStorey"]
    if ref:
        project = ref.by_type("IfcProject")[0]
        element.copy_deep(ref, new_model, project)
        context = ref.by_type("IfcGeometricRepresentationContext")[0]
    else:
        project = new_model.create_entity("IfcProject", GlobalId=ifcopenshell.guid.new(), Name="Sample Project", owner_history = create_owner_history(new_model))
        context = new_model.create_entity("IfcGeometricRepresentationContext", ContextType="Model", ContextIdentifier="Building Model")
    # Create_basic_skeleton
    def create():
        prev = None
        for item in spatial_hierachy:
            if item == "IfcProject":
                new_spatial_layer = project
                new_spatial_layer.RepresentationContexts = [context]
            else:
                new_spatial_layer = new_model.create_entity(item, GlobalId=ifcopenshell.guid.new(), Name= "Sample" + item)
            if prev != None:
                new_relationship = new_model.create_entity("IfcRelAggregates", GlobalId=ifcopenshell.guid.new(), RelatingObject=prev, RelatedObjects=[new_spatial_layer])
            prev = new_spatial_layer
        return new_model, prev
    return create()
def export(guids, model, file_path, save_props=True):
    # Step 1: Create new basic IFC project
    new_model, storey = create_basic_structure(ref=model)
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
    new_model.write(file_path)
    return new_model
# ====================================================================
# Creating new ifc geometry
# ====================================================================
def create_ifc_element_from_node(model, node):
    """
    Create an IFC element with geometry and property sets.

    :param model: ifcopenshell.file() object.
    :param element_type: e.g., "IfcWall", "IfcSlab", "IfcRoof"
    :param geom_info: dict with keys: T_matrix, vertex, faceVertexIndices, bbox
    :param psets: dict structured IFC property sets
    :param context: optional IfcGeometricRepresentationContext
    :return: The created IFC product
    """
    if  len(model.by_type("IfcGeometricRepresentationContext")) == 0:
        context = ifcopenshell.api.run("context.add_context", model, context_type="Model")
    else:
      context = model.by_type("IfcGeometricRepresentationContext")[0]


    # Step 1: Create the element
    element = model.create_entity(
        node.geom_type,
        GlobalId=node.guid,
        Name= node.name
    )
    # Step 2: Create the mesh geometry
    verts = node.geom_info["vertex"]
    faces = node.geom_info["faceVertexIndices"]
    # Create IfcCartesianPoints
    points = [model.create_entity("IfcCartesianPoint", Coordinates=pt.tolist()) for pt in verts]
    # Create IfcPolyLoops from face indices
    faces_loops = []
    for tri in faces:
        loop = model.create_entity("IfcPolyLoop", Polygon=[points[i] for i in tri])
        face_bound = model.create_entity("IfcFaceOuterBound", Bound=loop, Orientation=True)
        face = model.create_entity("IfcFace", Bounds=[face_bound])
        faces_loops.append(face)
    face_set = model.create_entity("IfcConnectedFaceSet", CfsFaces=faces_loops)
    shell = model.create_entity("IfcClosedShell", CfsFaces=faces_loops)
    shape_representation = model.create_entity(
        "IfcShapeRepresentation",
        ContextOfItems=context,
        RepresentationIdentifier="Body",
        RepresentationType="Faceted_Brep",
        Items=[model.create_entity("IfcFacetedBrep", Outer=shell)]
    )
    product_shape = model.create_entity("IfcProductDefinitionShape", Representations=[shape_representation])
    element.Representation = product_shape
    # Step 3: Place the element in 3D space
    transform = node.geom_info["T_matrix"]
    loc = model.create_entity("IfcCartesianPoint", Coordinates=transform[:3, 3].tolist())
    axis = model.create_entity("IfcDirection", DirectionRatios=transform[:3, 2].tolist())
    ref_direction = model.create_entity("IfcDirection", DirectionRatios=transform[:3, 1].tolist())
    placement = model.create_entity(
        "IfcAxis2Placement3D",
        Location=loc,
        Axis=axis,
        RefDirection=ref_direction
    )
    local_placement = model.create_entity(
    "IfcLocalPlacement",
    PlacementRelTo=None,
    RelativePlacement=placement
    )
    element.ObjectPlacement = local_placement
    # Step 4: Add Property Sets
    for pset_name, props in node.psets.items():
        prop_list = []
        for key, val in props.items():
            if isinstance(val, (int, float,str)):
                val_ifc = wrap_ifc_value(model, val)
                prop = model.create_entity("IfcPropertySingleValue", Name=key, NominalValue=val_ifc)
            else:
                continue
            prop_list.append(prop)
        pset = model.create_entity("IfcPropertySet", Name=pset_name, HasProperties=prop_list)
        model.create_entity(
            "IfcRelDefinesByProperties",
            GlobalId=ifcopenshell.guid.new(),
            RelatedObjects=[element],
            RelatingPropertyDefinition=pset
        )
    return element