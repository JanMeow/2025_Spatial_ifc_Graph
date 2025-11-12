import compute_proxy as CP
from utils import Graph
from sklearn.preprocessing import LabelEncoder
from pathlib import Path
import pickle
import xgboost as xgb
import pandas as pd
__version__ = "1.0.0"
BASEDIR = Path(__file__).resolve(strict= True).parent
model_0_path = BASEDIR / "model" / "model-intrinsic-0.1.0.pkl"
model_1_path = BASEDIR / "model" / "model-contextural-0.1.0.pkl"
#Manually label data
feature_enconder = {
    "None": 0,
    "IfcWall": 1,
    "IfcSlab": 2,
    "IfcRoof": 3,
    "IfcColumn": 4,
    "IfcBeam": 5,
    "IfcCurtainWall": 6,
    "IfcFooting": 7,
    "IfcPlate": 8
}
cols = ["upper", "lower", "left", "right"]

with open(model_0_path, "rb") as f0, open(model_1_path, "rb") as f1:
    model_0 = pickle.load(f0)
    model_1 = pickle.load(f1)

def predict_pipeline(graph: Graph):
    """
    This function is a placeholder for the data pipeline.
    It should contain the logic to process and prepare data for training or inference.
    """
    # First step inference
    X0 = pd.DataFrame([CP.get_Intrinsic_features(graph, k) for k in graph.node_dict.keys()])
    y0 = [node.geom_type for node in graph.node_dict.values()]
    preds_0 = model_0.predict(X0)
    # Convert predictions to labels
    le = LabelEncoder()
    le.fit_transform(y0)
    # Assigned type determined by model0 to the graph
    for node, pred in zip(graph.node_dict.values(), le.inverse_transform(preds_0)):
        node.geom_type = pred
    # Get Contextural feastures and econde the features using the feature_enconder
    # Note that the number in the feature_enconder do not atch the prediction classes
    X1 = pd.DataFrame([CP.get_contextural_features(graph, key) for key in graph.node_dict.keys()])
    for col in cols:
        X1[col] = X1[col].fillna("None")
        X1[col] = X1[col].map(feature_enconder)
    X_combined = pd.concat([X0, X1], axis=1)
    preds_1 = model_1.predict(X_combined)
    preds_1 = {k: label for k, label in zip(graph.node_dict.keys(), le.inverse_transform(preds_1))}
    return preds_1