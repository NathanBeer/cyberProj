"""
ML classifier for attack detection, trained on CSIC 2010 features.
"""
from __future__ import annotations

import joblib
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report

from .features import extract_features, requests_to_feature_matrix, FEATURE_NAMES

MODEL_PATH = Path(__file__).parent.parent / "models" / "classifier.joblib"


class AttackClassifier:
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
        )
        self.label_encoder = LabelEncoder()
        self.is_trained = False

    def train(self, requests: list[dict], labels: list[str], verbose: bool = True) -> dict:
        X = requests_to_feature_matrix(requests)
        y = self.label_encoder.fit_transform(labels)

        self.model.fit(X, y)
        self.is_trained = True

        if verbose:
            preds = self.model.predict(X)
            report = classification_report(
                y, preds, target_names=self.label_encoder.classes_
            )
            print("\nTraining classification report:\n", report)

        return {"classes": list(self.label_encoder.classes_), "n_samples": len(labels)}

    def predict(self, request: dict) -> dict:
        """
        Returns:
          {
            "label": "normal" | "anomalous",
            "confidence": float (0-1),
            "feature_importance": dict (top 5 features)
          }
        """
        if not self.is_trained:
            return self._rule_based_predict(request)

        features = np.array(list(extract_features(request).values()), dtype=float).reshape(1, -1)
        proba = self.model.predict_proba(features)[0]
        pred_idx = np.argmax(proba)
        label = self.label_encoder.inverse_transform([pred_idx])[0]
        confidence = float(proba[pred_idx])

        # Top contributing features for this prediction
        importances = self.model.feature_importances_
        feature_vals = extract_features(request)
        top_features = sorted(
            zip(FEATURE_NAMES, importances),
            key=lambda x: x[1],
            reverse=True,
        )[:5]

        return {
            "label": label,
            "confidence": confidence,
            "top_features": {name: feature_vals.get(name, 0) for name, _ in top_features},
        }

    def _rule_based_predict(self, request: dict) -> dict:
        """Fallback when no model is trained."""
        features = extract_features(request)
        attack_signals = (
            features["has_sql_keyword"]
            + features["has_xss"]
            + features["has_cmd_injection"]
            + features["has_path_traversal"]
            + features["has_ldap_pattern"]
        )
        if attack_signals > 0:
            return {"label": "anomalous", "confidence": min(0.6 + attack_signals * 0.1, 0.95), "top_features": {}}
        return {"label": "normal", "confidence": 0.75, "top_features": {}}

    def save(self, path: str | Path = MODEL_PATH):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"model": self.model, "encoder": self.label_encoder}, path)
        print(f"Model saved to {path}")

    @classmethod
    def load(cls, path: str | Path = MODEL_PATH) -> "AttackClassifier":
        path = Path(path)
        if not path.exists():
            instance = cls()
            return instance
        data = joblib.load(path)
        instance = cls()
        instance.model = data["model"]
        instance.label_encoder = data["encoder"]
        instance.is_trained = True
        return instance
