import pandas as pd
import xgboost as xgb
import pickle

# Dummy but real training data
data = pd.DataFrame([
    [5000, 30, 12000, 1, 0],
    [80000, 68, 5000, 4, 1],
    [20000, 45, 10000, 2, 0],
    [120000, 75, 4000, 4, 1],
    [15000, 35, 9000, 1, 0]
], columns=[
    "total_claim_amount",
    "insured_age",
    "policy_annual_premium",
    "incident_severity",
    "fraud"
])

X = data.drop("fraud", axis=1)
y = data["fraud"]

model = xgb.XGBClassifier(
    max_depth=3,
    n_estimators=50,
    learning_rate=0.1,
    eval_metric="logloss",
    random_state=42
)

model.fit(X, y)

# SAVE AS PKL
with open("C:/HopeAI/Course/8. AgenticAI/health_claim_agentic_ai/ml/fraud_model.pkl", "wb") as f:
    pickle.dump(model, f)

print(" XGBoost model saved as ml/fraud_model.pkl")
