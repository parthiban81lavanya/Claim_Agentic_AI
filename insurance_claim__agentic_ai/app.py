import os
import jwt
import datetime
from functools import wraps
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    make_response
)
from werkzeug.security import check_password_hash

#from claim_agents.orchestrator import Orchestrator
from orchestrator import Orchestrator
from db.database import (
    SessionLocal,
    init_db,
    Claim,
    AdminUser
)

# ---------------------------------------------------
# APP CONFIG
# ---------------------------------------------------

app = Flask(__name__)

SECRET_KEY = os.getenv("JWT_SECRET", "change-this-in-production")
JWT_EXPIRATION_MINUTES = 30

# Initialize DB tables
init_db()

# Initialize AI Orchestrator
#orchestrator = Orchestrator(use_llm_qa=False)
#orchestrator = Orchestrator(use_llm_qa=True)
orchestrator = Orchestrator()

# ---------------------------------------------------
# JWT AUTH DECORATOR
# ---------------------------------------------------

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("admin_token")

        if not token:
            return redirect(url_for("login"))

        try:
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except Exception:
            return redirect(url_for("login"))

        return f(*args, **kwargs)

    return decorated

# ---------------------------------------------------
# HOME PAGE
# ---------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")

# ---------------------------------------------------
# SUBMIT CLAIM
# ---------------------------------------------------

@app.route("/submit", methods=["POST"])
def submit_claim():

    db = SessionLocal()

    try:
        # -----------------------------
        # Collect form inputs
        # -----------------------------
        total_claim_amount = float(request.form.get("total_claim_amount") or 0)
        insured_age = int(request.form.get("insured_age") or 0)
        policy_annual_premium = float(request.form.get("policy_annual_premium") or 0)
       # incident_severity = request.form.get("incident_severity")
        incident_severity = int(request.form.get("incident_severity") or 0)
        policy_age_days = int(request.form.get("policy_age_days") or 0)
        previous_claims_count = int(request.form.get("previous_claims_count") or 0)
        hospital_risk_score = float(request.form.get("hospital_risk_score") or 0)
        is_emergency = int(request.form.get("is_emergency") or 0)

        # -----------------------------
        # Temporary Claim Object for AI
        # -----------------------------
        class TempClaim:
            pass

        claim_obj = TempClaim()
        claim_obj.claim_id = f"CLM-{datetime.datetime.now().timestamp()}"  #Claim id issue fix added
        claim_obj.customer_id = "CUS001" 
        claim_obj.claim_amount = total_claim_amount     #Claim id issue fix added
        claim_obj.total_claim_amount = total_claim_amount
        claim_obj.insured_age = insured_age
        claim_obj.policy_annual_premium = policy_annual_premium
        claim_obj.incident_severity = incident_severity
        claim_obj.policy_age_days = policy_age_days
        claim_obj.policy_duration_years = policy_age_days / 365
        claim_obj.previous_claims_count = previous_claims_count
        claim_obj.hospital_risk_score = hospital_risk_score
        #claim_obj.location_risk_score = location_risk_score
        claim_obj.is_emergency = is_emergency
        

        
        # -----------------------------
        # AI Processing
        # -----------------------------
        result = orchestrator.process_claim(claim_obj)

        final_status = result["status"]
        fraud_prob = result["fraud_score"]
        risk_level = result["risk_level"]
        reject_reason = result["reject_reason"]

        print("Fraud Score:", fraud_prob)
        print("Risk Level:", risk_level)
        print("Final Status:", final_status)

        # -----------------------------
        # Save to Database
        # -----------------------------
        claim_record = Claim(
            total_claim_amount=total_claim_amount,
            policy_annual_premium=policy_annual_premium,
            insured_age=insured_age,
            incident_severity=incident_severity,
            previous_claims_count=previous_claims_count,
            hospital_risk_score=hospital_risk_score,
            fraud_probability=fraud_prob,
            #status=risk_level,
            #final_decision=final_status,
            status=final_status,
            risk_level=risk_level,
            rejected_reason=reject_reason
        )

        db.add(claim_record)
        db.commit()

        # -----------------------------
        # Return result page
        # -----------------------------
        return render_template(
            "result.html",
            final_status=final_status,
            fraud_prob=round(fraud_prob, 4),
            risk_level=risk_level,
            rejected_reason=reject_reason
        )

    except Exception as e:
        db.rollback()
        return f"Error processing claim: {str(e)}"

    finally:
        db.close()

# ---------------------------------------------------
# ADMIN LOGIN
# ---------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        db = SessionLocal()

        try:
            email = request.form["email"]
            password = request.form["password"]

            admin = db.query(AdminUser).filter_by(email=email).first()

            if admin and check_password_hash(admin.password_hash, password):

                token = jwt.encode(
                    {
                        "admin_id": admin.id,
                        "exp": datetime.datetime.utcnow()
                        + datetime.timedelta(minutes=JWT_EXPIRATION_MINUTES)
                    },
                    SECRET_KEY,
                    algorithm="HS256"
                )

                response = make_response(redirect(url_for("admin_dashboard")))
                response.set_cookie(
                    "admin_token",
                    token,
                    httponly=True,
                    samesite="Lax"
                )

                return response

            return render_template("login.html", error="Invalid credentials")

        finally:
            db.close()

    return render_template("login.html")

# ---------------------------------------------------
# ADMIN DASHBOARD
# ---------------------------------------------------

@app.route("/admin")
@token_required
def admin_dashboard():

    db = SessionLocal()
    try:
        claims = db.query(Claim).order_by(Claim.id.desc()).all()
        

        # Normalize all old statuses
        for claim in claims:

            if not claim.status:
                claim.status = "PENDING_HUMAN_REVIEW"

            elif claim.status in ["Pending", "Manual Review","Review"]:
                claim.status = "PENDING_HUMAN_REVIEW"

            elif claim.status in ["Approved", "approved"]:
                claim.status = "APPROVED"

            elif claim.status in ["Rejected", "rejected"]:
                claim.status = "REJECTED"

        db.commit()

        # Now split properly
        pending_claims = [c for c in claims if c.status == "PENDING_HUMAN_REVIEW"]
        rejected_claims = [c for c in claims if c.status == "REJECTED"]
        approved_claims = [c for c in claims if c.status == "APPROVED"]

        return render_template(
            "admin.html",
            pending_claims=pending_claims,
            rejected_claims=rejected_claims,
            approved_claims=approved_claims,
            
        )

    finally:
        db.close()
        
@app.route("/approve/<int:claim_id>", methods=["POST"])
@token_required
def approve_claim(claim_id):

    db = SessionLocal()

    try:
        claim = db.query(Claim).filter(Claim.id == claim_id).first()

        if claim:
            claim.status = "APPROVED"
            claim.final_decision = "APPROVED"
            claim.needs_human_approval = False
            claim.rejected_reason = "Admin review completed and action taken"

            db.commit()

        return redirect(url_for("admin_dashboard"))
    finally:
        db.close()
@app.route("/reject/<int:claim_id>", methods=["POST"])
@token_required
def reject_claim(claim_id):

    db = SessionLocal()

    try:
        claim = db.query(Claim).filter(Claim.id == claim_id).first()

        if claim:
            claim.status = "REJECTED"
            claim.final_decision = "REJECTED"
            claim.needs_human_approval = False
            claim.rejected_reason = "Admin review completed and action taken"
            db.commit()

        return redirect(url_for("admin_dashboard"))
    finally:
        db.close()        
# -----------------------------------------
# LOGOUT
# ---------------------------------------------------

@app.route("/logout", methods=["POST"])
def logout():

    response = make_response(redirect(url_for("login")))
    response.set_cookie("admin_token", "", expires=0)
    return response

# ---------------------------------------------------
# RUN APPLICATION
# ---------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)