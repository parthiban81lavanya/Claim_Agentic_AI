# app.py

from flask import Flask, request, render_template, redirect, url_for, jsonify
from db.database import SessionLocal, Claim
from claim_agents.orchestrator import Orchestrator
from datetime import datetime

app = Flask(__name__)

# Use LLM QA
#orch = Orchestrator(use_llm_qa=True)
# Use QA
orch = Orchestrator(use_llm_qa=False)


# ====================================================
# 🏠 HOME PAGE
# ====================================================
@app.route("/")
def index():
    return render_template("index.html")


# ====================================================
# 📝 SUBMIT CLAIM
# ====================================================
@app.route("/submit_claim", methods=["POST"])
def submit_claim():
    db = SessionLocal()

    try:
        data = request.form

        # Create Claim Entry
        claim = Claim(
            total_claim_amount=float(data["total_claim_amount"]),
            policy_annual_premium=float(data["policy_annual_premium"]),
            insured_age=int(data["insured_age"]),
            incident_severity=data["incident_severity"],
            status="PROCESSING"
        )

        db.add(claim)
        db.commit()
        db.refresh(claim)

        # ===============================
        # 🤖 Run Agentic Flow
        # ===============================
        result = orch.process_claim(claim)
       
        dev_result = result["dev_result"]
        qa_result = result["qa_result"]

        # ===============================
        # 💾 SAVE ML RESULTS
        # ===============================
        claim.fraud_score = dev_result["fraud_score"]
        claim.ml_model_version = "xgboost_v1"

        # ===============================
        # 💾 SAVE QA RESULTS
        # ===============================
        claim.qa_notes = qa_result.get("reasoning", "Rule-based validation")
        claim.review_priority = qa_result.get("risk_level", "LOW")
        claim.llm_explanation = qa_result.get("reasoning")

        # ===============================
        #  HUMAN REVIEW LOGIC
        # ===============================
        if result["needs_human_approval"]:
            claim.status = "PENDING_HUMAN_REVIEW"
        else:
            claim.status = "APPROVED"
            claim.human_decision = "Auto-approved by AI"
            claim.approved_by = "SYSTEM"
            claim.approved_at = datetime.utcnow()

        db.commit()

        return render_template(
            "result.html",
            claim=claim,
            result=result
        )

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)})

    finally:
        db.close()


# ====================================================
# 👨‍⚖️ ADMIN DASHBOARD
# ====================================================
@app.route("/admin")
def admin_dashboard():
    db = SessionLocal()
    claims = db.query(Claim).order_by(Claim.created_at.desc()).all()
    db.close()

    return render_template("admin.html", claims=claims)


# ====================================================
# ✅ ADMIN APPROVE / REJECT
# ====================================================
@app.route("/admin/action/<int:claim_id>/<action>")
def admin_action(claim_id, action):
    db = SessionLocal()

    claim = db.query(Claim).filter(Claim.id == claim_id).first()

    if not claim:
        db.close()
        return "Claim not found"

    if action.upper() not in ["APPROVED", "REJECTED"]:
        db.close()
        return "Invalid action"

    claim.status = action.upper()
    claim.human_decision = f"Manually {action.upper()}"
    claim.approved_by = "ADMIN"
    claim.approved_at = datetime.utcnow()

    db.commit()
    db.close()

    return redirect(url_for("admin_dashboard"))


# ====================================================
# 📊 API ENDPOINT (Optional)
# ====================================================
@app.route("/api/claims")
def api_claims():
    db = SessionLocal()
    claims = db.query(Claim).all()
    db.close()

    return jsonify([
        {
            "id": c.id,
            "amount": c.total_claim_amount,
            "fraud_score": c.fraud_score,
            "priority": c.review_priority,
            "status": c.status
        }
        for c in claims
    ])


# ====================================================
# 🚀 RUN APP
# ====================================================
if __name__ == "__main__":
    app.run(debug=True)
