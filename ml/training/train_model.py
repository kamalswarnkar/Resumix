import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import SGDClassifier


def train(input_csv: Path, artifact_dir: Path):
    data = pd.read_csv(input_csv)
    data = data.dropna(subset=["text", "role"])
    data = data.drop_duplicates(subset=["text", "role"])

    X = data["text"].astype(str)
    y = data["role"].astype(str)

    encoder = LabelEncoder()
    y_encoded = encoder.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )

    candidates = {
        "logreg": LogisticRegression(max_iter=3000, class_weight="balanced"),
        "linear_svc": CalibratedClassifierCV(
            estimator=LinearSVC(class_weight="balanced"),
            method="sigmoid",
            cv=3,
        ),
        "sgd_hinge": SGDClassifier(loss="hinge", alpha=1e-5, max_iter=3000, random_state=42),
    }

    best_name = None
    best_pipeline = None
    best_f1 = -1.0
    best_accuracy = -1.0

    for name, classifier in candidates.items():
        pipeline = Pipeline(
            steps=[
                (
                    "tfidf",
                    TfidfVectorizer(
                        max_features=30000,
                        ngram_range=(1, 3),
                        min_df=2,
                        sublinear_tf=True,
                    ),
                ),
                ("clf", classifier),
            ]
        )

        pipeline.fit(X_train, y_train)
        preds = pipeline.predict(X_test)
        acc = accuracy_score(y_test, preds)
        f1 = f1_score(y_test, preds, average="macro")

        if f1 > best_f1:
            best_f1 = f1
            best_accuracy = acc
            best_name = name
            best_pipeline = pipeline

    vectorizer = best_pipeline.named_steps["tfidf"]
    model = best_pipeline.named_steps["clf"]

    artifact_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, artifact_dir / "role_classifier.pkl")
    joblib.dump(vectorizer, artifact_dir / "tfidf_vectorizer.pkl")
    joblib.dump(encoder, artifact_dir / "label_encoder.pkl")

    print(f"Rows used: {len(data)}")
    print(f"Best model: {best_name}")
    print(f"Validation accuracy: {best_accuracy:.2%}")
    print(f"Validation macro F1: {best_f1:.2%}")


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
