import time
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util
import ifcopenshell.util.element as element
from geometry_processing import get_local_coors
from collections import deque
import numpy as np
import trimesh
# ====================================================================
# Trimesh Export for pure geometry viewing
# ====================================================================
def export_trimesh(graph, guids, file_path):
    scene = trimesh.Scene()
    for guid in guids:
        node = graph.node_dict[guid]
        v,f = node.geom_info["vertices"], node.geom_info["faces"]
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
# ====================================================================
#  Copying the original spatial strcutures/ containers into new model
# ====================================================================
def copy_project_structure(old_model, max_depth=10):
    """
    Create a new IFC model by copying the spatial structure from old_model,
    stopping the recursion at max_depth.
    
    Typical depth levels (for example):
      0: IfcProject
      1: IfcSite
      2: IfcBuilding
      3: IfcBuildingStorey
    """
    new_model = ifcopenshell.file(schema=old_model.schema)
    old_project = old_model.by_type("IfcProject")[0]
    new_project = copy_spatial_structure(old_model, new_model, old_project, depth=0, max_depth=max_depth)
    
    # Copy the geometric representation contexts
    old_contexts = old_model.by_type("IfcGeometricRepresentationContext")
    for ctx in old_contexts:
        new_model.add(ctx)
    
    return new_model

def copy_spatial_structure(old_model, new_model, old_object, depth, max_depth):
    """
    Recursively copies an IFC object and its spatial children up to max_depth.
    
    Parameters:
      old_model: The source IFC file.
      new_model: The target IFC file.
      old_object: The current IFC object to copy.
      depth: Current recursion depth.
      max_depth: Maximum depth to recurse into. If depth == max_depth,
                 child objects are not copied.
    """
    indent = "  " * depth
    print(f"{indent}Copying {old_object.is_a()} with GUID: {old_object.GlobalId} at depth {depth}")
    
    # Step A: Copy the current object (shallow copy; omit 'id')
    new_object = copy_entity(new_model, old_object, except_attrs=["id"])
    # new_object = ifcopenshell.util.element.copy_deep(old_model, old_object)
    
    # Optionally, you might extract properties here if desired.
    # extract_properties(old_model, new_model, new_object.GlobalId)
    
    # Step B: If we have not reached the maximum depth, copy children via IfcRelAggregates.
    if depth < max_depth:
        for old_rel in old_object.IsDecomposedBy:
            if old_rel.is_a("IfcRelAggregates"):
                new_children = []
                for old_child in old_rel.RelatedObjects:
                    child_copy = copy_spatial_structure(old_model, new_model, old_child, depth=depth+1, max_depth=max_depth)
                    new_children.append(child_copy)
                new_rel = copy_rel(new_model, old_rel, new_object, new_children)
    else:
        print(f"{indent}-- Max depth reached for {old_object.is_a()} with GUID: {old_object.GlobalId}")
    
    return new_object

def copy_entity(new_model, current_entity, except_attrs=["id"]):
    # Copy shallow spatial structure entities, by default id is ignored cause its autogenrated
    attrs = current_entity.get_info()
    entity_type = attrs.pop("type") 
    attrs = {k: v for k, v in attrs.items() if k not in except_attrs}
    return new_model.create_entity(entity_type, **attrs)
def copy_rel(new_model, rel, relating, related):
    return new_model.create_entity(
        "IfcRelAggregates",
        GlobalId=ifcopenshell.guid.new(),
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
def partial_export(guids, model, file_path, save_props=True, take_ref = False):
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
def create_shape(new_model, entity,vertices, faces, shape = "IfcTriangulatedFaceSet"):
    if shape == "IfcTriangulatedFaceSet":
        return create_triangulated_faceset(new_model, entity, vertices, faces)
    elif shape == "IfcFacetedBrep":
        return create_IfcFacetedBrep(new_model, entity, vertices, faces)
    elif shape == "PolygonalFaceSet":
        return create_polygon_faceset(new_model, entity, vertices, faces)
def create_triangulated_faceset(new_model, entity, vertices, faces):
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
    return entity
def create_IfcFacetedBrep(new_model, entity, vertices, faces):

    # Create an IfcCartesianPoint for each vertex.
    point_entities = []
    for vertex in vertices:
        pt = new_model.create_entity("IfcCartesianPoint", Coordinates=tuple(vertex.tolist()))
        point_entities.append(pt)

    # For each face, create an IfcPolyLoop and then an IfcFace.
    face_entities = []
    for face in faces:
        # Get the corresponding IfcCartesianPoint objects.
        face_points = [point_entities[i] for i in face]
        # Create an IfcPolyLoop with these points.
        polyloop = new_model.create_entity("IfcPolyLoop", Polygon=face_points)
        # Wrap the loop in an IfcFaceOuterBound (set Orientation to True).
        face_bound = new_model.create_entity("IfcFaceOuterBound", Bound=polyloop, Orientation=True)
        # Create an IfcFace with this boundary.
        face_entity = new_model.create_entity("IfcFace", Bounds=[face_bound])
        face_entities.append(face_entity)

    # Create an IfcClosedShell with the list of faces.
    closed_shell = new_model.create_entity("IfcClosedShell", CfsFaces=face_entities)
    # Create an IfcFacetedBrep with the closed shell as its Outer.
    brep = new_model.create_entity("IfcFacetedBrep", Outer=closed_shell)

    # Retrieve the geometric representation context from the new model.
    context = new_model.by_type("IfcGeometricRepresentationContext")[0]

    # Create an IfcShapeRepresentation using the Brep.
    shape_rep = new_model.create_entity(
        "IfcShapeRepresentation",
        ContextOfItems=context,
        RepresentationIdentifier="Body",
        RepresentationType="Brep",  # Represent as a B-rep
        Items=[brep]
    )
    # Create the IfcProductDefinitionShape and assign it to the entity.
    prod_def_shape = new_model.create_entity("IfcProductDefinitionShape", Representations=[shape_rep])
    entity.Representation = prod_def_shape
    return entity
def create_polygon_faceset(new_model, entity, vertices, faces):

     # Convert vertices to a list of lists (float values)
    vertex_list = vertices.astype(float).tolist()
    
    # Create an IfcCartesianPointList3D to hold vertex coordinates.
    point_list = new_model.create_entity("IfcCartesianPointList3D", CoordList=vertex_list)
    
    # Create IfcIndexedPolygonalFace entities for each face.
    face_entities = []
    for face in faces:
        # Convert face indices to 1-based (IFC requires 1-based indexing).
        try:
            face_indices = (face + 1).tolist()
        except Exception:
            face_indices = [idx + 1 for idx in face]
        
        # Create an IfcIndexedPolygonalFace with attribute CoordIndex.
        indexed_face = new_model.create_entity("IfcIndexedPolygonalFace", CoordIndex=face_indices)
        face_entities.append(indexed_face)
    
    # Create the IfcPolygonalFaceSet using the "Faces" attribute.
    poly_face_set = new_model.create_entity(
        "IfcPolygonalFaceSet",
        Coordinates=point_list,
        Closed=True,
        Faces=face_entities
    )
    
    # Retrieve the geometric representation context.
    context = new_model.by_type("IfcGeometricRepresentationContext")[0]
    
    # Create an IfcShapeRepresentation with RepresentationType "Tessellation"
    # (which is typical even for B-reps, though the underlying geometry is a polygonal face set).
    shape_rep = new_model.create_entity(
        "IfcShapeRepresentation",
        ContextOfItems=context,
        RepresentationIdentifier="Body",
        RepresentationType="Tessellation",
        Items=[poly_face_set]
    )
    
    # Create an IfcProductDefinitionShape and assign it to the entity.
    prod_def_shape = new_model.create_entity("IfcProductDefinitionShape", Representations=[shape_rep])
    entity.Representation = prod_def_shape
    return entity

# ====================================================================
# Creating and Assign properties from old model to new model
# ====================================================================
def create_psets_from_node(node, new_model):
    """
    Given a 'node' whose 'node.psets' is a dictionary of the form:
        {
          "Pset_WallCommon": { "Reference": "Basic Wall", "IsExternal": True },
          "BaseQuantities": { "Length": 3000, "Height": 2800 }
        }
    ...create corresponding property definition entities (IfcPropertySet or IfcElementQuantity)
    in 'new_model'. Return a list of newly created entities.
    """
    pset_entities = []
    if node.psets == None:
        return pset_entities  # no psets to create

    # For each Pset name -> subdict of properties
    for pset_name, props_dict in node.psets.items():
        # If we detect "BaseQuantities" (or any other name you want),
        # we create an IfcElementQuantity; otherwise we create an IfcPropertySet.
        if pset_name == "BaseQuantities":
            eq = _create_ifc_element_quantity(new_model, pset_name, props_dict)
            if eq:
                pset_entities.append(eq)
        else:
            pset_entity = _create_ifc_property_set(new_model, pset_name, props_dict)
            if pset_entity:
                pset_entities.append(pset_entity)
    return pset_entities
def assign_psets_to_entity(new_model, new_entity, psets_list):
    """
    Given a list of IfcPropertyDefinition entities (IfcPropertySet or IfcElementQuantity),
    attach each to 'new_entity' via a new IfcRelDefinesByProperties relationship.
    """
    for prop_def in psets_list:
        new_model.create_entity(
            "IfcRelDefinesByProperties",
            GlobalId=ifcopenshell.guid.new(),
            RelatedObjects=[new_entity],
            RelatingPropertyDefinition=prop_def
        )
def _create_ifc_property_set(new_model, pset_name, props_dict):
    """
    Create an IfcPropertySet with IfcPropertySingleValue properties from 'props_dict'.
    """
    # Build a list of IfcPropertySingleValue
    property_list = []
    for key, val in props_dict.items():
        # If there's a key you want to skip, like "id", you can do:
        if key == "id":
            continue

        value_entity = to_ifc_value(new_model, val)
        prop_sv = new_model.create_entity(
            "IfcPropertySingleValue",
            Name=key,
            NominalValue=value_entity,
            Unit=None
        )
        property_list.append(prop_sv)
    # Create the IfcPropertySet itself
    if not property_list:
        return None  # no properties to attach
    pset_entity = new_model.create_entity(
        "IfcPropertySet",
        GlobalId=ifcopenshell.guid.new(),
        Name=pset_name,
        Description=None,
        HasProperties=property_list
    )
    return pset_entity
def _create_ifc_element_quantity(new_model, qset_name, quantity_dict):
    """
    Create an IfcElementQuantity with IfcQuantityLength / IfcQuantityArea / etc.
    This is a simple heuristic that checks key names for "Length", "Area", or "Volume".
    """
    quantity_list = []
    for key, val in quantity_dict.items():
        # skip "id" if present
        if key == "id":
            continue

        # Convert numeric value
        num_val = float(val) if val is not None else 0.0

        if "Length" in key:
            qty = new_model.create_entity(
                "IfcQuantityLength",
                Name=key,
                Description=None,
                Unit=None,
                LengthValue=num_val
            )
        elif "Area" in key:
            qty = new_model.create_entity(
                "IfcQuantityArea",
                Name=key,
                Description=None,
                Unit=None,
                AreaValue=num_val
            )
        elif "Volume" in key:
            qty = new_model.create_entity(
                "IfcQuantityVolume",
                Name=key,
                Description=None,
                Unit=None,
                VolumeValue=num_val
            )
        else:
            # fallback or skip
            # you can create IfcQuantityLength by default, or skip
            continue

        quantity_list.append(qty)

    if not quantity_list:
        return None

    eq = new_model.create_entity(
        "IfcElementQuantity",
        GlobalId=ifcopenshell.guid.new(),
        Name=qset_name,
        MethodOfMeasurement=None,
        Quantities=quantity_list
    )
    return eq
def to_ifc_value(new_model, py_val):
    if isinstance(py_val, bool):
        ifc_type = "IfcBoolean"
    elif isinstance(py_val, int):
        ifc_type = "IfcInteger"
    elif isinstance(py_val, float):
        ifc_type = "IfcReal"
    elif isinstance(py_val, str):
        ifc_type = "IfcLabel"
    else:
        # Fallback: treat everything else as string
        ifc_type = "IfcLabel"
    return new_model.create_entity(ifc_type, py_val)

# ====================================================================
# Extracting properties from old model to new model might crash as some
# internal referneces might no be copied.
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
                GlobalId=ifcopenshell.guid.new(),
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
    element = model.by_guid(guid)
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
                                GlobalId=ifcopenshell.guid.new(), 
                                RelatingStructure=new_container, 
                                RelatedElements=[new_entity])
    else:
        print(f"Warning: Could not find container for element {guid}.")
        return 
def modify_element_to_model(old_model, new_model, graph, guid, vertices=None, faces=None):
    node = graph.node_dict[guid]
    old_entity = old_model.by_guid(guid)
    new_entity =  copy_entity(new_model, old_entity, except_attrs=["id", "ObjectPlacement", "Representation"])
    # === Create shape representation for the element
    create_shape(new_model, new_entity,vertices, faces)
    # # === Create and assign properties from the old element: 
    # extract_properties(old_model, new_model, guid)
    # pset_defs = create_psets_from_node(node, new_model)
    # assign_psets_to_entity(new_model, new_entity, pset_defs)
    # === Attach new element to same spatial container
    assign_to_container(old_model, new_model, guid)
    print(f"✅ Created new ifc entity for element {guid} with {len(vertices)} vertices and {len(faces)} faces.")
    return element
# Temporary function.
def create_element_in_model(new_model, graph, guid, vertices=None, faces=None, shape = None):
    node = graph.node_dict[guid]
    new_entity = new_model.create_entity(node.geom_type, 
                                         GlobalId=node.guid, 
                                         Name=node.name)
    create_shape(new_model, new_entity,vertices, faces, shape = shape)
    new_container = new_model.by_type("IfcBuildingStorey")[0]
    storey = new_model.by_type("IfcBuildingStorey")[0]
    new_model.create_entity("IfcRelContainedInSpatialStructure", 
                                GlobalId=ifcopenshell.guid.new(), 
                                RelatingStructure=new_container, 
                                RelatedElements=[new_entity])
