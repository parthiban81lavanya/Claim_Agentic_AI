import json
import os
from datetime import datetime


class AuditAgent:

    reviewer="Admin"

    def __init__(self, log_file="audit_logs.json"):
        self.log_file = log_file

        # Create log file if it doesn't exist
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                json.dump([], f)

        print("AuditAgent initialized")

    # =====================================================
    # MAIN AUDIT FUNCTION
    # =====================================================
    def log_decision(
        self,
        claim,
        dev_result,
        qa_result,
        final_status,
        agent_used,
        reviewer="Admin"
    ):

        audit_record = {
            "timestamp": datetime.now().isoformat(),
            # "claim_id": claim.get("claim_id"),
            # "customer_id": claim.get("customer_id"),
            # "claim_amount": claim.get("claim_amount"),

            # "fraud_score": dev_result.get("fraud_score"),
            # "risk_level": dev_result.get("risk_level"),

            # "qa_status": qa_result.get("status"),
            # "qa_reasoning": qa_result.get("reasoning"),

            "claim_id": claim.claim_id,
            "customer_id": claim.customer_id,
            "claim_amount": claim.claim_amount,
            "fraud_score": dev_result.get("fraud_score"),
            "risk_level": qa_result.get("risk_level"),

                "qa_status": qa_result.get("status"),
                "qa_reasoning": qa_result.get("reasoning"),

            "agent_used": agent_used,
            "final_status": final_status,

            "reviewer": reviewer
        }

        self._write_log(audit_record)

        return audit_record

    # =====================================================
    # WRITE LOG TO FILE
    # =====================================================
    def _write_log(self, record):

        try:
            with open(self.log_file, "r") as f:
                logs = json.load(f)

            logs.append(record)

            with open(self.log_file, "w") as f:
                json.dump(logs, f, indent=4)

            print("Audit log recorded")

        except Exception as e:
            print("Audit logging failed:", str(e))

    # =====================================================
    # OPTIONAL: VIEW LOGS
    # =====================================================
    def get_all_logs(self):

        try:
            with open(self.log_file, "r") as f:
                logs = json.load(f)
            return logs
        except:
            return []

    # =====================================================
    # OPTIONAL: CLEAR LOGS
    # =====================================================
    def clear_logs(self):

        with open(self.log_file, "w") as f:
            json.dump([], f)

        print("Audit logs cleared")