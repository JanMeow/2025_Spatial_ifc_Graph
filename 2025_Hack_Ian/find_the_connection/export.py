import time
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util
import ifcopenshell.util.element as element
from geometry_processing import get_local_coors
from collections import deque
import numpy as np
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
def reset_placement_to_origin(model, element):
    origin = model.create_entity("IfcCartesianPoint", Coordinates=[0.0, 0.0, 0.0])
    placement_3d = model.create_entity("IfcAxis2Placement3D", Location=origin)
    local_placement = model.create_entity("IfcLocalPlacement", RelativePlacement=placement_3d)
    element.ObjectPlacement = local_placement
# ====================================================================
def copy_spatial_structure(old_model, new_model, old_object):
    # Step A: Copy the current object
    new_object = copy_entity(new_model, old_object)
    # Step B: For each 'IfcRelAggregates' in old_object.IsDecomposedBy
    #         we create a new relationship that references all child copies at once
    for old_rel in old_object.IsDecomposedBy:
        # We only want relationships that are actually a decomposition
        if old_rel.is_a("IfcRelAggregates"):
            # Gather the new copies of all child objects
            new_children = []
            for old_child in old_rel.RelatedObjects:
                new_child = copy_spatial_structure(old_model, new_model, old_child)
                new_children.append(new_child)
            
            # Now create a new relationship in the new model, referencing parent + children
            new_rel = copy_rel(new_model, old_rel, new_object, new_children)
    # Return the new copy of this object to the caller
    return new_object
def copy_project_structure(old_model):
    new_model = ifcopenshell.file(schema=old_model.schema)
    old_project = old_model.by_type("IfcProject")[0]
    new_project = copy_spatial_structure(old_model, new_model, old_project)
    return new_model
def copy_entity(new_model, current_entity):
    # Copy shallow spatial structure entities
    attrs = current_entity.get_info()
    entity_type = attrs.pop("type") 
    attrs.pop("id") 
    return new_model.create_entity(entity_type, **attrs)
def copy_rel(new_model, rel, relating, related):
    return new_model.create_entity(
        "IfcRelAggregates",
        GlobalId=rel.GlobalId,
        RelatingObject=relating,
        RelatedObjects=related
    )
def copy_element_props_subgraph(old_model, new_model, guid):
    old_element = old_model.by_guid(guid)
    subgraph = old_model.traverse(old_element)
    skip_root_types = ["IfcProject", "IfcSite", "IfcBuilding", "IfcBuildingStorey" ,"IfcGeometricRepresentationContext"]
    for obj in subgraph[1:]:
        if obj.is_a("IfcRoot"):
            if obj.is_a() in skip_root_types:
                # do not copy project, site, building, storey, or context
                continue
            # If it's not skipped, check if we already have an object with that GlobalId
            if new_model.by_guid(obj.GlobalId):
                continue
            # Then add it
            new_model.add(obj)
        else:
            new_model.add(obj)
    return 
def create_project_structure( schema = "IFC4"):
    new_model = ifcopenshell.file(schema = schema)
    spatial_hierachy = ["IfcProject","IfcSite", "IfcBuilding", "IfcBuildingStorey"]

    # Create_basic_skeleton
    def create():
        prev = None
        for item in spatial_hierachy:
            if item == "IfcProject":
                new_spatial_layer = new_model.create_entity("IfcProject", GlobalId=ifcopenshell.guid.new(), Name="Sample Project", OwnerHistory = create_owner_history(new_model))
                new_spatial_layer.RepresentationContexts = [new_model.create_entity("IfcGeometricRepresentationContext", ContextType="Model", ContextIdentifier="Building Model")]
            else:
                new_spatial_layer = new_model.create_entity(item, GlobalId=ifcopenshell.guid.new(), Name= "Sample" + item)
            if prev != None:
                new_relationship = new_model.create_entity("IfcRelAggregates", GlobalId=ifcopenshell.guid.new(), RelatingObject=prev, RelatedObjects=[new_spatial_layer])
            prev = new_spatial_layer
        return new_model, prev
    return create()
def export(guids, model, file_path, save_props=True, take_ref = False):
    # Step 1: Create new basic IFC project
    if take_ref:
        new_model, storey = create_project_structure(ref=model)
    else:
        new_model, storey = create_project_structure()
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
    new_model.write(file_path)
    return new_model
# ====================================================================
# Creating new ifc geometry
# ====================================================================
def create_shape(new_model, entity,vertices, faces):
    vertex_list = vertices.astype(float).tolist()
    # IFC requires 1-based indices
    face_list = (faces + 1).astype(int).tolist()
    # === Create IfcCartesianPointList3D
    point_list = new_model.create_entity("IfcCartesianPointList3D", CoordList=vertex_list)
    # === Create IfcTriangulatedFaceSet
    face_set = new_model.create_entity(
        "IfcTriangulatedFaceSet",
        Coordinates=point_list,
        CoordIndex=face_list,
        Closed=True)
    # === Create IfcShapeRepresentation
    context = new_model.by_type("IfcGeometricRepresentationContext")[0]
    shape_rep = new_model.create_entity(
        "IfcShapeRepresentation",
        ContextOfItems=context,
        RepresentationIdentifier="Body",
        RepresentationType="Tessellation",
        Items=[face_set])
    # === Create IfcProductDefinitionShape
    prod_def_shape = new_model.create_entity("IfcProductDefinitionShape", Representations=[shape_rep])
    # === Replace the geometry on the element
    entity.Representation = prod_def_shape
    return 
# ====================================================================
# Extracting properties from old model to new model
# ====================================================================
def extract_properties(old_model, new_model, guid):
    old_entity = old_model.by_guid(guid)
    new_entity = new_model.by_guid(guid)
    # Go through all relationships that define property sets
    for rel in getattr(old_entity, "IsDefinedBy", []):
        if not rel.is_a("IfcRelDefinesByProperties"):
            continue
        old_pset = rel.RelatingPropertyDefinition
        new_pset = _copy_single_pset(old_pset, new_model)
        if new_pset:
            # Create a brand-new relationship in new_model
            new_model.create_entity(
                "IfcRelDefinesByProperties",
                GlobalId=rel.GlobalId,
                RelatedObjects=[new_entity],
                RelatingPropertyDefinition=new_pset)
    return
def _copy_single_pset(old_pset, new_model):
    """Copy a single pset or quantity set from old_pset to new_model."""
    if not old_pset:
        return None
    # Already copied?
    if hasattr(old_pset, "GlobalId"):
        try:
            existing = new_model.by_guid(old_pset.GlobalId)
            if existing:
                return existing
        except:
            if old_pset.is_a("IfcTypeObject"):
                print("hhahaha")
                return None
            if old_pset.is_a("IfcPropertySet"):
                return _copy_ifc_property_set(old_pset, new_model)
            elif old_pset.is_a("IfcElementQuantity"):
                return _copy_ifc_element_quantity(old_pset, new_model)
            else:
                # Can expand to handle more property set types
                print(f"Skipping Pset type: {old_pset.is_a()}")
                return None
def _copy_ifc_property_set(old_pset, new_model):
    """Copies an IfcPropertySet and its IfcPropertySingleValue objects."""
    new_properties = []
    for prop in old_pset.HasProperties:
        if prop.is_a("IfcPropertySingleValue"):
            new_prop = new_model.create_entity(
                "IfcPropertySingleValue",
                Name=prop.Name,
                Description=prop.Description,
                NominalValue=prop.NominalValue,
                Unit=prop.Unit
            )
            new_properties.append(new_prop)
        else:
            # Could handle IfcComplexProperty, etc., if needed
            pass

    new_pset = new_model.create_entity(
        "IfcPropertySet",
        GlobalId=old_pset.GlobalId,
        Name=old_pset.Name,
        Description=old_pset.Description,
        HasProperties=new_properties
    )
    return new_pset
def _copy_ifc_element_quantity(old_eq, new_model):
    """Copies an IfcElementQuantity and its IfcPhysicalQuantity sub-objects."""
    new_quantities = []
    for q in old_eq.Quantities:
        # e.g. IfcQuantityLength, IfcQuantityArea, IfcQuantityVolume, ...
        new_q = new_model.create_entity(
            q.is_a(),
            Name=q.Name,
            Description=q.Description,
            Unit=q.Unit,
            # Each quantity type has its own attribute (LengthValue, AreaValue, etc.)
            LengthValue=getattr(q, "LengthValue", None),
            AreaValue=getattr(q, "AreaValue", None),
            VolumeValue=getattr(q, "VolumeValue", None),
            # etc. for other quantity subtypes
        )
        new_quantities.append(new_q)

    new_elem_qty = new_model.create_entity(
        "IfcElementQuantity",
        GlobalId=old_eq.GlobalId,
        Name=old_eq.Name,
        Description=old_eq.Description,
        MethodOfMeasurement=old_eq.MethodOfMeasurement,
        Quantities=new_quantities
    )
    return new_elem_qty
# ====================================================================
# Combining extracting psets and crearing new shape representation
# ====================================================================
def get_container_rel(model, guid):
    for rel in model.by_type("IfcRelContainedInSpatialStructure"):
        if guid in [e.GlobalId for e in rel.RelatedElements]:
            return rel
    return None
def assign_to_container(old_model, new_model, guid):
    old_rel = get_container_rel(old_model, guid)
    old_container = old_rel.RelatingStructure
    new_container = new_model.by_guid(old_container.GlobalId)
    new_entity = new_model.by_guid(guid)
    if new_container:
        new_model.create_entity("IfcRelContainedInSpatialStructure", 
                                GlobalId=old_rel.GlobalId, 
                                RelatingStructure=new_container, 
                                RelatedElements=[new_entity])
    else:
        print(f"Warning: Could not find container for element {guid}.")
        return 
def modify_element_to_model(old_model, new_model, guid, vertices=None, faces=None):
    old_entity = old_model.by_guid(guid)
    new_entity =  copy_entity(new_model, old_entity)
    # # === Copy properties from the old element: still working on it
    # extract_properties(old_model, new_model, guid)
    # === Create shape representation for the element
    create_shape(new_model, new_entity,vertices, faces)
    # === Attach new element to same spatial container
    assign_to_container(old_model, new_model, guid)
    print(f"✅ Created new ifc entity for element {guid} with {len(vertices)} vertices and {len(faces)} faces.")
    return element
