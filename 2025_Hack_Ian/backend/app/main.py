from typing import Union
from fastapi import FastAPI, UploadFile, File
import boto3
import logging
from botocore.exceptions import ClientError
import ifcopenshell
import tempfile
from utils import Graph
from pydantic import BaseModel, field_validator, Field
from typing import Optional, List, Dict, Any, ForwardRef
import numpy as np
from model import predict_pipeline
# Data Scehma Definition
#========================================================================
# class NodeSchema(BaseModel):
#     name:str
#     guid: str
#     geom_type: str
#     geom_info: Optional[Dict[str]] = None
#     pset: Optional[Dict[str]] = None
#     near: List[str] = Field(default_factory=list)

#     @field_validator("geom_info", mode = "before")
#     def convert_numpy_arrays(cls, v):
#         if isinstance(v, dict):
#             return {
#                 k: v_ if not isinstance(v_, np.ndarray) else v_.tolist()
#                 for k, v_ in v.items()
#             }
#         return v

# NodeSchema.model_rebuild()
# Api Definition
#========================================================================
app = FastAPI()
s3 = boto3.resource('s3')
#========================================================================
@app.get("/")
def home():
    return {"health_check": "ok", "model_version": "1.0.0"}
@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
@app.post("/upload_ifc")
def upload_ifc(file: UploadFile = File(...), bucket: str = "2025dokwood"):
    # Upload the file
    s3_client = boto3.client('s3')
    object_name = file.filename
    try:
        response = s3_client.upload_fileobj(file.file, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    logging.info(f"File {object_name} uploaded to bucket {bucket}.")
    return {"message": "File uploaded successfully", "file_name": object_name}
@app.post("/ifc_to_graph/{file_name}")
def ifc_to_graph(file_name:str, bucket: str = "2025dokwood"):
    s3_client = boto3.client('s3')
    try:
        response = s3_client.get_object(Bucket = bucket, Key = file_name)
    except ClientError as e:
        logging.error(e)
        return {"error": "File not found in S3 bucket."} 
    body = response['Body'].read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".ifc") as tmp_file:
        tmp_file.write(body)
        tmp_file_path = tmp_file.name
    model = ifcopenshell.open(tmp_file_path)
    root = model.by_type("IfcProject")[0]
    graph = Graph.create(root)
    graph.build_bvh()   
    for node in graph.node_dict.values():
        if node.geom_info != None:
            node.near = [guid for guid in graph.bvh_query(node.geom_info["bbox"])
                         if guid != node.guid]
    # guid = "1GQtQBII1Ciel1nBYV7cFW"
    # node = graph[guid]
    # print(node.near)
    return  {"message": "Graph created successfully", 
             "node_count": len(graph.node_dict),
             "body": {k: v.near for k, v in graph.node_dict.items() }}
@app.post("/ifc_type_predict/{file_name}")
def ifc_type_predict(file_name: str, bucket: str = "2025dokwood"):
    s3_client = boto3.client('s3')
    try:
        response = s3_client.get_object(Bucket = bucket, Key = file_name)
    except ClientError as e:
        logging.error(e)
        return {"error": "File not found in S3 bucket."} 
    body = response['Body'].read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".ifc") as tmp_file:
        tmp_file.write(body)
        tmp_file_path = tmp_file.name
    model = ifcopenshell.open(tmp_file_path)    
    root = model.by_type("IfcProject")[0]
    graph = Graph.create(root)
    graph.build_bvh()   
    for node in graph.node_dict.values():
        if node.geom_info != None:
            node.near = [graph[guid] for guid in graph.bvh_query(node.geom_info["bbox"])
                         if guid != node.guid]       
    preds = predict_pipeline(graph)
    return {"pred": preds}