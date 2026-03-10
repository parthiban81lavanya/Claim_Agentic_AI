class QAAgent:

    def validate(self, claim, dev_result):

        fraud_score = dev_result["fraud_score"]
        risk_level = "LOW"
        needs_human = False
        reasoning = []

        # Rule 1: High fraud score
        if fraud_score >= 0.85:
            risk_level = "HIGH"
            reasoning.append("Fraud score extremely high.")
        elif fraud_score >= 0.60:
            risk_level = "MEDIUM"
            reasoning.append("Fraud score moderately high.")

        else:
            risk_level = "LOW"    

        # Rule 2: Very high claim ratio
        claim_ratio = claim.total_claim_amount / claim.policy_annual_premium
        if claim_ratio > 12:
            risk_level = "HIGH"
            reasoning.append("Claim ratio unusually high.")

        # Rule 3: Too many previous claims
        if claim.previous_claims_count > 5:
            needs_human = True
            reasoning.append("Multiple previous claims detected.")

        # Rule 4: Young age high severity
        if claim.insured_age < 23 and claim.incident_severity >= 3:
            needs_human = True
            reasoning.append("Young claimant with severe incident.")

        return {
            "risk_level": risk_level,
            "needs_human_approval": needs_human,
            "reasoning": " | ".join(reasoning) if reasoning else "No major QA flags"
        }