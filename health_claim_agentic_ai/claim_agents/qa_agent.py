class QAAgent:
    """
    Rule-based QA agent.
    Acts as a safety gate before human approval.
    """


class QAAgent:

    def validate(self, claim, dev_result):

        fraud_score = dev_result.get("fraud_score", 0)
        decision = dev_result.get("decision", "APPROVE")

        needs_human = False
        reasoning = []
        risk_level = "LOW"

        # Rule 1: High fraud score
        if fraud_score >= 0.85:
            needs_human = True
            risk_level = "HIGH"
            reasoning.append("Fraud score exceeds 0.85 threshold")

        # Rule 2: ML says REVIEW
        if decision == "REVIEW":
            needs_human = True
            risk_level = "MEDIUM"
            reasoning.append("ML model flagged for review")

        if not reasoning:
            reasoning.append("Claim passed rule-based QA checks")

        return {
            "needs_human_approval": needs_human,
            "reasoning": " | ".join(reasoning),
            "risk_level": risk_level
        }
