import argparse
from pathlib import Path

import joblib
import pandas as pd
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
    matthews_corrcoef,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

MODEL_RATIONALE = {
    "logreg": "Strong linear baseline for sparse text; stable and interpretable coefficients with probabilistic outputs.",
    "svm": "Effective margin-based classifier for text data, especially in high-dimensional TF-IDF spaces.",
    "xgboost": "Powerful boosted-tree ensemble to capture non-linear patterns and feature interactions.",
    "random_forest": "Bagged tree ensemble baseline with robustness against overfitting compared to single trees.",
    "knn": "Instance-based non-parametric baseline to compare local-neighborhood behavior.",
    "decision_tree": "Simple non-linear baseline with high interpretability.",
}

MODEL_PREFERENCE = {
    "logreg": 1,
    "svm": 2,
    "xgboost": 3,
    "random_forest": 4,
    "knn": 5,
    "decision_tree": 6,
}


def _get_model_scores(y_train, train_preds, y_test, test_preds, score_values):
    scores = {
        "train_accuracy": accuracy_score(y_train, train_preds),
        "test_accuracy": accuracy_score(y_test, test_preds),
        "balanced_accuracy": balanced_accuracy_score(y_test, test_preds),
        "precision_macro": precision_score(y_test, test_preds, average="macro", zero_division=0),
        "recall_macro": recall_score(y_test, test_preds, average="macro", zero_division=0),
        "f1_macro": f1_score(y_test, test_preds, average="macro", zero_division=0),
        "precision_weighted": precision_score(y_test, test_preds, average="weighted", zero_division=0),
        "recall_weighted": recall_score(y_test, test_preds, average="weighted", zero_division=0),
        "f1_weighted": f1_score(y_test, test_preds, average="weighted", zero_division=0),
        "mcc": matthews_corrcoef(y_test, test_preds),
    }

    if score_values is not None:
        try:
            auc = roc_auc_score(y_test, score_values, multi_class="ovr", average="macro")
            scores["roc_auc_ovr_macro"] = auc
        except Exception:
            scores["roc_auc_ovr_macro"] = None
    else:
        scores["roc_auc_ovr_macro"] = None

    return scores


def _build_markdown_report(results_df, selected_row):
    metric_columns = [
        "model",
        "train_accuracy",
        "test_accuracy",
        "balanced_accuracy",
        "precision_macro",
        "recall_macro",
        "f1_macro",
        "precision_weighted",
        "recall_weighted",
        "f1_weighted",
        "mcc",
        "roc_auc_ovr_macro",
    ]
    table_df = results_df[metric_columns].copy()
    for col in metric_columns[1:]:
        table_df[col] = table_df[col].apply(lambda v: "N/A" if pd.isna(v) else f"{float(v):.4f}")

    header = "| " + " | ".join(metric_columns) + " |"
    divider = "| " + " | ".join(["---"] * len(metric_columns)) + " |"
    rows = [
        "| " + " | ".join(str(row[col]) for col in metric_columns) + " |"
        for _, row in table_df.iterrows()
    ]
    table_lines = [header, divider, *rows]
    selected_line = (
        f"Selected model: **{selected_row['model']}**\n\n"
        f"Selection reason: It achieved the highest macro F1 ({selected_row['f1_macro']:.4f}). "
        "Tie-breakers were weighted F1, balanced accuracy, and test accuracy. "
        "If still tied, model preference favors stable linear models with reliable probability behavior."
    )
    return "\n".join(
        [
            "# Model Comparison Report",
            "",
            "## Why these models",
            "All selected models are proven baselines for high-dimensional sparse text vectors (TF-IDF), "
            "covering linear, margin-based, tree-ensemble, and instance-based classification families.",
            "",
            "## Metrics Comparison",
            *table_lines,
            "",
            "## Model Rationales",
            *[f"- **{name}**: {reason}" for name, reason in MODEL_RATIONALE.items()],
            "",
            "## Selection Decision",
            selected_line,
        ]
    )


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
        "random_forest": RandomForestClassifier(
            n_estimators=400,
            random_state=42,
            class_weight="balanced_subsample",
            n_jobs=1,
        ),
        "xgboost": XGBClassifier(
            objective="multi:softprob",
            eval_metric="mlogloss",
            n_estimators=250,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.9,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=1,
            verbosity=0,
        ),
        "knn": KNeighborsClassifier(n_neighbors=5, weights="distance", metric="cosine", n_jobs=1),
        "decision_tree": DecisionTreeClassifier(random_state=42, class_weight="balanced"),
        "svm": SVC(kernel="linear", class_weight="balanced", probability=True, random_state=42),
    }

    best_name = ""
    best_pipeline = None
    results = []

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
        train_preds = pipeline.predict(X_train)
        test_preds = pipeline.predict(X_test)
        score_values = None
        if hasattr(pipeline, "predict_proba"):
            score_values = pipeline.predict_proba(X_test)
        elif hasattr(pipeline, "decision_function"):
            score_values = pipeline.decision_function(X_test)

        model_scores = _get_model_scores(y_train, train_preds, y_test, test_preds, score_values)
        model_scores["model"] = name
        model_scores["reason_for_inclusion"] = MODEL_RATIONALE.get(name, "Text classification baseline.")
        results.append(model_scores)

    results_df = pd.DataFrame(results)
    results_df["preference_rank"] = results_df["model"].map(MODEL_PREFERENCE).fillna(999).astype(int)
    rank_columns = ["f1_macro", "f1_weighted", "balanced_accuracy", "test_accuracy"]
    results_df = results_df.sort_values(
        rank_columns + ["preference_rank"],
        ascending=[False, False, False, False, True],
    ).reset_index(drop=True)
    best_name = str(results_df.loc[0, "model"])

    for name, classifier in candidates.items():
        if name == best_name:
            best_pipeline = Pipeline(
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
            best_pipeline.fit(X_train, y_train)
            break

    vectorizer = best_pipeline.named_steps["tfidf"]
    model = best_pipeline.named_steps["clf"]

    artifact_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, artifact_dir / "role_classifier.pkl")
    joblib.dump(vectorizer, artifact_dir / "tfidf_vectorizer.pkl")
    joblib.dump(encoder, artifact_dir / "label_encoder.pkl")
    results_df.to_csv(artifact_dir / "model_comparison.csv", index=False)

    selected_row = results_df.iloc[0]
    markdown_report = _build_markdown_report(results_df, selected_row)
    (artifact_dir / "model_comparison.md").write_text(markdown_report, encoding="utf-8")

    print(f"Rows used: {len(data)}")
    print(f"Best model: {best_name}")
    print(f"Train accuracy: {selected_row['train_accuracy']:.2%}")
    print(f"Validation accuracy: {selected_row['test_accuracy']:.2%}")
    print(f"Validation macro F1: {selected_row['f1_macro']:.2%}")
    print(f"Comparison CSV: {artifact_dir / 'model_comparison.csv'}")
    print(f"Comparison Report: {artifact_dir / 'model_comparison.md'}")


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
