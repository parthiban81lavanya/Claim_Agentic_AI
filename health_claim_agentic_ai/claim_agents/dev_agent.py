import pickle
import numpy as np
import os

class DevAgent:
    """
    ML-backed Dev Agent with strict feature ordering and validation.
    """

    FEATURE_ORDER = [
        "total_claim_amount",
        "policy_annual_premium",
        "insured_age",
        "incident_severity"
    ]

    def __init__(self):
        model_path = os.path.join("ml", "fraud_model.pkl")

        if not os.path.exists(model_path):
            raise FileNotFoundError("fraud_model.pkl not found")

        with open(model_path, "rb") as f:
            self.model = pickle.load(f)

        self.model_version = "xgboost_v1"

    def evaluate_claim(self, claim):
        # Feature validation
        for feature in self.FEATURE_ORDER:
            if getattr(claim, feature, None) is None:
                raise ValueError(f"Missing required feature: {feature}")

        X = np.array([[
            claim.total_claim_amount,
            claim.policy_annual_premium,
            claim.insured_age,
            claim.incident_severity
        ]], dtype=float)

        prob = self.model.predict_proba(X)[0][1]

        fraud_score = round(float(prob), 3)
        decision = "REVIEW" if fraud_score > 0.7 else "APPROVED"

        claim.ml_model_version = self.model_version

        return {
            "fraud_score": fraud_score,
            "decision": decision,
            "model_version": self.model_version
        }

