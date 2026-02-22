from pathlib import Path
import joblib

BASE_DIR = Path(__file__).resolve().parent
ARTIFACT_DIR = BASE_DIR / "artifacts"
MODEL_PATH = ARTIFACT_DIR / "role_classifier.pkl"
VECTORIZER_PATH = ARTIFACT_DIR / "tfidf_vectorizer.pkl"
ENCODER_PATH = ARTIFACT_DIR / "label_encoder.pkl"


def predict_role(text: str) -> str:
    if not MODEL_PATH.exists() or not VECTORIZER_PATH.exists() or not ENCODER_PATH.exists():
        return "Model not trained"

    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
    encoder = joblib.load(ENCODER_PATH)

    X = vectorizer.transform([text])
    pred = model.predict(X)[0]
    return str(encoder.inverse_transform([pred])[0])
