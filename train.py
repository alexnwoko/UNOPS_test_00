"""
Train a binary disaster-tweet classifier (TF-IDF + Logistic Regression).

Why this approach:
- Tiny CPU-only artifact (~MBs), fast cold start and <100ms inference -> fits
  Cloud Run free tier and the 2s p95 latency requirement comfortably.
- Reliably beats the 0.70 F1 baseline on the disaster class for this dataset.

Outputs:
- model.joblib : a fitted sklearn Pipeline (vectorizer + calibrated classifier)
- prints held-out and cross-validated F1 on the disaster (label=1) class.
"""
import sys
import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import f1_score, classification_report
from textclean import clean  # shared preprocessor (importable -> picklable)

DATA = sys.argv[1] if len(sys.argv) > 1 else "train.csv"


def build_pipeline() -> Pipeline:
    word_vec = TfidfVectorizer(
        preprocessor=clean, analyzer="word", ngram_range=(1, 2),
        min_df=2, max_df=0.9, sublinear_tf=True, strip_accents="unicode",
    )
    char_vec = TfidfVectorizer(
        preprocessor=clean, analyzer="char_wb", ngram_range=(3, 5),
        min_df=2, sublinear_tf=True,
    )
    features = FeatureUnion([("word", word_vec), ("char", char_vec)])
    base = LogisticRegression(C=1.0, max_iter=2000, class_weight="balanced")
    # Calibrate so the returned `score` is a meaningful probability in [0,1].
    clf = CalibratedClassifierCV(base, method="sigmoid", cv=5)
    return Pipeline([("features", features), ("clf", clf)])


def main():
    df = pd.read_csv(DATA)
    df = df.dropna(subset=["text", "target"]).copy()
    df["target"] = df["target"].astype(int)
    X, y = df["text"].values, df["target"].values
    print(f"Loaded {len(df)} rows | positives={y.mean():.3f}")

    # Held-out evaluation
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    pipe = build_pipeline()
    pipe.fit(X_tr, y_tr)
    pred = pipe.predict(X_te)
    f1 = f1_score(y_te, pred, pos_label=1)
    print(f"\nHeld-out F1 (disaster class) = {f1:.4f}")
    print(classification_report(y_te, pred, digits=3))

    # Cross-validated F1 for a robust estimate
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv = cross_val_score(build_pipeline(), X, y, cv=skf,
                         scoring="f1")  # f1 of positive class by default
    print(f"5-fold CV F1 (disaster) = {cv.mean():.4f} +/- {cv.std():.4f}")

    # Refit on ALL data for the deployed artifact and save
    final = build_pipeline()
    final.fit(X, y)
    joblib.dump(final, "model.joblib")
    print("\nSaved model.joblib")
    # quick smoke test
    for t in ["Forest fire near La Ronge Sask. Canada",
              "I love this sunny weather, going to the beach!"]:
        p = final.predict_proba([t])[0][1]
        print(f"  score={p:.3f}  label={int(p>=0.5)}  <- {t!r}")


if __name__ == "__main__":
    main()
