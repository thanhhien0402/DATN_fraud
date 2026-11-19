import os
import joblib


BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

MODEL_DIR = os.path.join(BASE_DIR, "models")


def load_xgboost_artifacts():
    model_path = os.path.join(MODEL_DIR, "xgboost.pkl")
    threshold_path = os.path.join(
        MODEL_DIR, "xgboost_threshold.txt"
    )
    encoder_path = os.path.join(MODEL_DIR, "encoder.pkl")
    features_path = os.path.join(
        MODEL_DIR, "xgboost_features.pkl"
    )

    model = joblib.load(model_path)
    encoder = joblib.load(encoder_path)
    model_features = joblib.load(features_path)

    with open(threshold_path, "r") as file:
        threshold = float(file.read().strip())

    return model, encoder, model_features, threshold