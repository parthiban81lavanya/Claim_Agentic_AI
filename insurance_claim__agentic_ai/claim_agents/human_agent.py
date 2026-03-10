class HumanAgent:

    def review(self, claim, dev_result, qa_result):
        """
        Simulates human review decision logic.
        In production this would be replaced by:
        - Internal review dashboard
        - API call
        - Manual approval workflow
        """

        fraud_score = dev_result.get("fraud_score", 0)
        risk_level = qa_result.get("risk_level", "LOW")

        # -----------------------------
        # Human decision logic
        # -----------------------------

        if fraud_score > 0.85 or risk_level == "HIGH":
            status = "REJECTED"
            notes = "High fraud confidence. Rejected by HumanAgent."

        elif fraud_score > 0.75:
            status = "APPROVED_WITH_INVESTIGATION"
            notes = "Approved but flagged for investigation."

        else:
            status = "APPROVED"
            notes = "Low fraud risk. Approved by HumanAgent."

        return {
            "claim_id": claim.claim_id,
            "status": status,
            "reject_reason": notes,
            "reviewed_by": "HumanAgent",
            "fraud_score": fraud_score,
            "risk_level": risk_level
        }