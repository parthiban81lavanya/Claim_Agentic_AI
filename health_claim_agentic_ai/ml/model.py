import pickle
import numpy as np

class FraudModel:
    def __init__(self, model_path="ml/fraud_model.pkl"):
        with open(model_path, "rb") as f:
            self.model = pickle.load(f)

    def predict(self, claim):
        X = np.array([[
            claim.total_claim_amount,
            claim.insured_age,
            claim.policy_annual_premium,
            claim.incident_severity
        ]])

        prob = self.model.predict_proba(X)[0][1]
        print(type(self.model))
        return float(round(prob, 2))
