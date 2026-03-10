import pickle
import numpy as np


class FraudModel:
    def __init__(self, model_path="ml/fraud_model.pkl"):
        with open(model_path, "rb") as f:
            self.model = pickle.load(f)

    def _extract_features(self, claim):
        """
        Supports:
        - SQLAlchemy Claim object
        - Dictionary input
        """

        if isinstance(claim, dict):
            total_claim_amount = float(claim.get("total_claim_amount", 0))
            insured_age = int(claim.get("insured_age", 0))
            policy_annual_premium = float(claim.get("policy_annual_premium", 0))
            incident_severity = int(claim.get("incident_severity", 0))
            policy_age_days = int(claim.get("policy_age_days", 0))
            previous_claims_count = int(claim.get("previous_claims_count", 0))
            hospital_risk_score = float(claim.get("hospital_risk_score", 0))
            is_emergency = int(claim.get("is_emergency", 0))

        else:
            # ORM object
            total_claim_amount = float(claim.total_claim_amount)
            insured_age = int(claim.insured_age)
            policy_annual_premium = float(claim.policy_annual_premium)
            incident_severity = int(claim.incident_severity)
            policy_age_days = int(claim.policy_age_days)
            previous_claims_count = int(claim.previous_claims_count)
            hospital_risk_score = float(claim.hospital_risk_score)
            is_emergency = int(claim.is_emergency)

        return np.array([[
            total_claim_amount,
            insured_age,
            policy_annual_premium,
            incident_severity,
            policy_age_days,
            previous_claims_count,
            hospital_risk_score,
            is_emergency
        ]])

    def predict(self, claim):
        """
        Returns fraud probability as float
        """

        X = self._extract_features(claim)

        # Predict fraud probability (class 1)
        prob = self.model.predict_proba(X)[0][1]
        print("Fraud probability",prob)
        return round(float(prob), 2)