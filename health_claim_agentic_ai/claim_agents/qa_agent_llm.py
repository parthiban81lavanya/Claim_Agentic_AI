import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class QAAgentLLM:
    """
    LLM-powered QA Agent.
    Provides reasoning, NOT decisions.
    """

    def validate(self, claim, dev_result):
        prompt = f"""
        You are an insurance QA auditor.

        Analyze the claim and identify risks.
        DO NOT approve or reject the claim.
        Only assess review priority.

        Claim:
        - Claim Amount: {claim.total_claim_amount}
        - Policy Premium: {claim.policy_annual_premium}
        - Insured Age: {claim.insured_age}
        - Incident Severity: {claim.incident_severity}
        - Fraud Score: {claim.fraud_score}

        Respond ONLY in JSON:
        {{
          "priority": "LOW | MEDIUM | HIGH",
          "concerns": "text explanation"
        }}
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        result = eval(response.choices[0].message.content)

        claim.qa_notes = f"LLM QA: {result['concerns']}"

        # LLM never decides outcome
        claim.status = "PENDING_HUMAN_REVIEW"
        claim.review_priority = result["priority"]

        return True
