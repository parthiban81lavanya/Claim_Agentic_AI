import pickle
#import joblib
import numpy as np


class DevAgent:

    def __init__(self):
    
     with open("C:/HopeAI/Course/8. AgenticAI/insurance_claim_ai/ml/fraud_model.pkl", "rb") as f: 
     #with open("ml/fraud_model.pkl", "rb") as f:    
        model_package = pickle.load(f)

## Updated for numpy version mismatch with docker
    # model_package = joblib.load("ml/fraud_model.pkl")
        self.model = None
        self.scaler = None

        # --------------------------------------------
        # Case 1: Model saved directly
        # --------------------------------------------
        if hasattr(model_package, "predict_proba"):
            self.model = model_package

        # --------------------------------------------
        # Case 2: Dictionary structure
        # --------------------------------------------
        elif isinstance(model_package, dict):

            # Nested structure: { "model": { "classifier": ..., "scaler": ... } }
            if isinstance(model_package.get("model"), dict):
                inner = model_package["model"]
                self.model = inner.get("classifier")
                self.scaler = inner.get("scaler")

            # Structure: { "model": sklearn_model }
            elif hasattr(model_package.get("model"), "predict_proba"):
                self.model = model_package.get("model")
                self.scaler = model_package.get("scaler")

            # Structure: { "classifier": sklearn_model }
            elif hasattr(model_package.get("classifier"), "predict_proba"):
                self.model = model_package.get("classifier")
                self.scaler = model_package.get("scaler")

        # --------------------------------------------
        # Final Safety Check
        # --------------------------------------------
        if not hasattr(self.model, "predict_proba"):
            raise ValueError(
                "Loaded object is not a valid sklearn model. "
                "Check how fraud_model.pkl was saved."
            )

    # -------------------------------------------------
    # CLAIM EVALUATION
    # -------------------------------------------------
    def evaluate_claim(self, claim):

        claim_ratio = (
            claim.total_claim_amount / claim.policy_annual_premium
            if claim.policy_annual_premium > 1000 else 0
        )

        features = np.array([[

            claim.total_claim_amount,
            claim.policy_annual_premium,
            claim.insured_age,
            #1 if claim.incident_severity == "HIGH" else 0,
            claim.incident_severity,
            claim.policy_duration_years,
            claim.previous_claims_count,
            claim.is_emergency,
            claim.hospital_risk_score
            #claim_ratio

        ]])

        # Apply scaler if exists
        if self.scaler is not None:
            features = self.scaler.transform(features)

        fraud_probability = float(
            self.model.predict_proba(features)[0][1]
        )
        risk_level = "LOW"
        decision = "APPROVE"
        
        # Decision Logic
        if fraud_probability >= 0.95:
            decision = "REJECT" ,
            risk_level = "HIGH"   # this should check with Human agent
            
        elif fraud_probability >= 0.65:
            decision = "REVIEW"   # this should check with QA_LLM 
            risk_level = "MEDIUM"
        else:
            decision = "APPROVE"  # this shoudl call QA_agent

        return {
            "decision": decision,
            "fraud_score": fraud_probability,
            "risk_level" : risk_level
        }


# -------------------------------------------------
# TEST BLOCK (Run this file directly to test)
# -------------------------------------------------
if __name__ == "__main__":

    class DummyClaim:
        def __init__(self):
        #     self.total_claim_amount = 120000
        #     self.policy_annual_premium = 20000
        #     self.insured_age = 45
        #     self.incident_severity = 4
        #     self.policy_duration_years = 4
        #     self.previous_claims_count = 2
        #    # self.location_risk_score = 0.7
        #     self.hospital_risk_score = 0.6
        #     self.is_emergency = 0

            self.total_claim_amount = 110000
            self.insured_age = 37
            self.policy_annual_premium = 15000
            self.incident_severity = 3
            self.policy_duration_years = 2
            self.previous_claims_count = 2
            self.hospital_risk_score = 0.7
            self.is_emergency = 1
            

    agent = DevAgent()
    claim = DummyClaim()

    result = agent.evaluate_claim(claim)
    print("Result:", result)