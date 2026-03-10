import pandas as pd
import numpy as np
import xgboost as xgb
import pickle
#import joblib
import os

from sklearn.model_selection import train_test_split, StratifiedKFold, RandomizedSearchCV
from sklearn.metrics import classification_report, roc_auc_score
from scipy.stats import randint, uniform

# =========================================
# Reproducibility
# =========================================
np.random.seed(42)
rows = 5000

# =========================================
# Generate Synthetic Insurance Data
# =========================================
data = pd.DataFrame({
    "total_claim_amount": np.random.randint(2000, 250000, rows),
    "insured_age": np.random.randint(18, 80, rows),
    "policy_annual_premium": np.random.randint(3000, 25000, rows),
    "incident_severity": np.random.randint(1, 5, rows),
    "policy_age_days": np.random.randint(10, 3650, rows),
    "previous_claims_count": np.random.randint(0, 8, rows),
    "hospital_risk_score": np.round(np.random.uniform(0, 1, rows), 2),
    "is_emergency": np.random.randint(0, 2, rows)
})

# =========================================
# Fraud Risk Simulation (Non-linear)
# =========================================
risk_score = (
    (data["total_claim_amount"] / 250000) * 0.35 +
    (data["incident_severity"] / 4) * 0.15 +
    (data["previous_claims_count"] / 8) * 0.15 +
    (1 - (data["policy_age_days"] / 3650)) * 0.15 +
    data["hospital_risk_score"] * 0.10 +
    (data["is_emergency"] * 0.10)
)

risk_score += (
    (data["total_claim_amount"] > 150000) &
    (data["incident_severity"] >= 3)
) * 0.15

risk_score += np.random.normal(0, 0.05, rows)

fraud_probability = 1 / (1 + np.exp(-8 * (risk_score - 0.5)))
data["fraud"] = (fraud_probability > 0.5).astype(int)

# =========================================
# Features
# =========================================
FEATURE_COLUMNS = [
    "total_claim_amount",
    "insured_age",
    "policy_annual_premium",
    "incident_severity",
    "policy_age_days",
    "previous_claims_count",
    "hospital_risk_score",
    "is_emergency"
]

X = data[FEATURE_COLUMNS]
y = data["fraud"]

# =========================================
# Train/Test Split
# =========================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    stratify=y,
    random_state=42
)

# =========================================
# Hyperparameter Space
# =========================================
param_dist = {
    "max_depth": randint(3, 10),
    "n_estimators": randint(150, 400),
    "learning_rate": uniform(0.01, 0.2),
    "subsample": uniform(0.6, 0.4),
    "colsample_bytree": uniform(0.6, 0.4),
    "gamma": uniform(0, 5),
    "min_child_weight": randint(1, 10)
}

# =========================================
# Base Model
# =========================================
base_model = xgb.XGBClassifier(
    eval_metric="logloss",
    random_state=42,
    # use_label_encoder=False
)

# =========================================
# Stratified K-Fold CV
# =========================================
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

random_search = RandomizedSearchCV(
    estimator=base_model,
    param_distributions=param_dist,
    n_iter=25,
    scoring="roc_auc",
    cv=cv,
    verbose=1,
    random_state=42,
    n_jobs=-1
)

# =========================================
# Train with Hyperparameter Search
# =========================================
random_search.fit(X_train, y_train)

best_model = random_search.best_estimator_

print("\nBest Parameters:")
print(random_search.best_params_)

# =========================================
# Evaluation
# =========================================
y_pred = best_model.predict(X_test)
y_prob = best_model.predict_proba(X_test)[:, 1]

print("\nClassification Report:\n")
print(classification_report(y_test, y_pred))

print("ROC-AUC Score:", roc_auc_score(y_test, y_prob))

# =========================================
# Save Model
# =========================================
os.makedirs("ml", exist_ok=True)

model_package = {
    "model": best_model,
    "features": FEATURE_COLUMNS,
    "version": "3.0.0_tuned"
}

with open("fraud_model.pkl", "wb") as f:
     pickle.dump(model_package, f)
# updated for numpy version mismatch in the training and docker.
#joblib.dump(model_package, "fraud_model.pkl")    

print("\nTuned fraud model saved successfully.")