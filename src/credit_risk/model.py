
from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    brier_score_loss,
    classification_report,
    confusion_matrix,
    roc_curve,
    precision_recall_curve,
)
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.credit_risk.woe import calculate_woe_iv


ROOT = Path(__file__).resolve().parents[2]

FEATURES = [
    "loan_amnt",
    "annual_inc",
    "dti",
    "int_rate",
    "emp_length",
]

TARGET = "default"
THRESHOLD = 0.50


def validate_dataset(df):
    """Check that the dataset has the required columns and target."""

    required = FEATURES + [TARGET]
    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(
            f"Dataset is missing required columns: {missing}"
        )

    df = df.copy()

    for col in FEATURES:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df[TARGET] = pd.to_numeric(df[TARGET], errors="coerce")

    if df[TARGET].isna().any():
        raise ValueError("The default target contains missing values.")

    if not set(df[TARGET].unique()).issubset({0, 1}):
        raise ValueError("The default target must contain only 0 and 1.")

    if df[TARGET].nunique() != 2:
        raise ValueError("The dataset must contain both default classes.")

    return df


def train_model(csv_path=None):
    """Train, evaluate and save the credit risk model."""

    csv_path = Path(
        csv_path or ROOT / "data/raw/loans_synthetic.csv"
    )

    if not csv_path.exists():
        raise FileNotFoundError(
            f"Loan dataset not found: {csv_path}"
        )

    df = validate_dataset(pd.read_csv(csv_path))

    X = df[FEATURES]
    y = df[TARGET].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    # Preprocessing
    prep = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
    ])

    # Logistic Regression model
    model = Pipeline([
        ("prep", prep),
        (
            "classifier",
            LogisticRegression(
                max_iter=1500,
                class_weight="balanced",
                random_state=42,
            ),
        ),
    ])

    model.fit(X_train, y_train)

    # Cross-validation on training data only
    min_class_count = int(y_train.value_counts().min())
    cv_scores = []

    if min_class_count >= 2:
        cv_folds = min(5, min_class_count)

        scores = cross_val_score(
            model,
            X_train,
            y_train,
            cv=cv_folds,
            scoring="roc_auc",
        )

        cv_scores = [float(score) for score in scores]

    # WoE / IV diagnostics on training data only
    reports_dir = ROOT / "reports"
    models_dir = ROOT / "models"

    reports_dir.mkdir(parents=True, exist_ok=True)
    models_dir.mkdir(parents=True, exist_ok=True)

    woe_table = calculate_woe_iv(
        X_train,
        y_train,
        FEATURES,
    )

    woe_table.to_csv(
        reports_dir / "woe_iv_analysis.csv",
        index=False,
    )

    # Predictions
    probabilities = model.predict_proba(X_test)[:, 1]
    predictions = (probabilities >= THRESHOLD).astype(int)

    # Evaluation metrics
    metrics = {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "balanced_accuracy": float(
            balanced_accuracy_score(y_test, predictions)
        ),
        "precision": float(
            precision_score(y_test, predictions, zero_division=0)
        ),
        "recall": float(
            recall_score(y_test, predictions, zero_division=0)
        ),
        "f1_score": float(
            f1_score(y_test, predictions, zero_division=0)
        ),
        "roc_auc": float(
            roc_auc_score(y_test, probabilities)
        ),
        "pr_auc": float(
            average_precision_score(y_test, probabilities)
        ),
        "brier_score": float(
            brier_score_loss(y_test, probabilities)
        ),
        "threshold": THRESHOLD,
        "cross_validation_roc_auc": cv_scores,
        "cv_mean_roc_auc": (
            float(np.mean(cv_scores)) if cv_scores else None
        ),
        "classification_report": classification_report(
            y_test,
            predictions,
            output_dict=True,
            zero_division=0,
        ),
        "confusion_matrix": confusion_matrix(
            y_test,
            predictions,
        ).tolist(),
        "test_rows": int(len(y_test)),
    }

    # Save test predictions
    prediction_results = X_test.copy()
    prediction_results["actual_default"] = y_test
    prediction_results["predicted_default"] = predictions
    prediction_results["default_probability"] = probabilities

    prediction_results.to_csv(
        reports_dir / "credit_risk_predictions.csv",
        index=False,
    )

    # Save ROC curve data
    fpr, tpr, roc_thresholds = roc_curve(
        y_test,
        probabilities,
    )

    pd.DataFrame({
        "false_positive_rate": fpr,
        "true_positive_rate": tpr,
        "threshold": roc_thresholds,
    }).to_csv(
        reports_dir / "roc_curve_data.csv",
        index=False,
    )

    # Save Precision-Recall curve data
    precision_values, recall_values, pr_thresholds = (
        precision_recall_curve(y_test, probabilities)
    )

    pd.DataFrame({
        "precision": precision_values[:-1],
        "recall": recall_values[:-1],
        "threshold": pr_thresholds,
    }).to_csv(
        reports_dir / "precision_recall_data.csv",
        index=False,
    )

    # Save feature coefficients
    classifier = model.named_steps["classifier"]

    coefficients = pd.DataFrame({
        "feature": FEATURES,
        "coefficient": classifier.coef_[0],
    })

    coefficients["absolute_importance"] = (
        coefficients["coefficient"].abs()
    )

    coefficients.sort_values(
        "absolute_importance",
        ascending=False,
    ).to_csv(
        reports_dir / "feature_importance.csv",
        index=False,
    )

    # Save model and metrics
    joblib.dump(
        model,
        models_dir / "credit_risk_model.joblib",
    )

    (reports_dir / "model_metrics.json").write_text(
        json.dumps(metrics, indent=2),
        encoding="utf-8",
    )

    return model, metrics


def score_customers(df):
    """Calculate model-estimated risk and risk bands."""

    model_path = ROOT / "models/credit_risk_model.joblib"

    if not model_path.exists():
        raise FileNotFoundError(
            "Trained model not found. Run train_model() first."
        )

    missing = [col for col in FEATURES if col not in df.columns]

    if missing:
        raise ValueError(
            f"Customer data is missing columns: {missing}"
        )

    model = joblib.load(model_path)

    out = df.copy()
    X = out[FEATURES].copy()

    for col in FEATURES:
        X[col] = pd.to_numeric(X[col], errors="coerce")

    probabilities = model.predict_proba(X)[:, 1]

    out["default_probability"] = probabilities

    out["risk_band"] = pd.cut(
        probabilities,
        bins=[-0.001, 0.10, 0.30, 1.001],
        labels=["Low", "Medium", "High"],
        include_lowest=True,
    ).astype(str)

    # Illustrative 300-850 risk score.
    # This is not an official credit bureau score.
    out["risk_score"] = (
        850 - probabilities * 550
    ).round().astype(int)

    return out
