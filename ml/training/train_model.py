import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder


def train(input_csv: Path, artifact_dir: Path):
    data = pd.read_csv(input_csv)
    data = data.dropna(subset=["text", "role"])

    X = data["text"].astype(str)
    y = data["role"].astype(str)

    encoder = LabelEncoder()
    y_encoded = encoder.fit_transform(y)

    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    X_vec = vectorizer.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_vec, y_encoded, test_size=0.3, random_state=42
    )

    model = LogisticRegression(max_iter=2000)
    model.fit(X_train, y_train)
    accuracy = model.score(X_test, y_test)

    artifact_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, artifact_dir / "role_classifier.pkl")
    joblib.dump(vectorizer, artifact_dir / "tfidf_vectorizer.pkl")
    joblib.dump(encoder, artifact_dir / "label_encoder.pkl")

    print(f"Model trained successfully. Accuracy: {accuracy:.2%}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train role prediction model")
    parser.add_argument(
        "--input",
        default=str(Path(__file__).resolve().parent / "sample_dataset.csv"),
        help="Path to training CSV with columns: text,role",
    )
    parser.add_argument(
        "--artifact-dir",
        default=str(Path(__file__).resolve().parents[1] / "artifacts"),
        help="Directory where trained artifacts will be stored",
    )
    args = parser.parse_args()

    train(Path(args.input), Path(args.artifact_dir))
