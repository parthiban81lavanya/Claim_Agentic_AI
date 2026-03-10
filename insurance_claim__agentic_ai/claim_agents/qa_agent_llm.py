from dotenv import load_dotenv
import os
import json
#from openai import OpenAI
import google.generativeai as genai

load_dotenv()


class QAAgentLLM:
#use this for OpenAI
    # def __init__(self):
    #     api_key = os.getenv("OPENAI_API_KEY")
    #     if not api_key:
    #         print("WARNING: OPENAI_API_KEY not found. LLM will not run.")
    #     self.client = OpenAI(api_key=api_key)

#use this for google api
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            print("WARNING: GEMINI_API_KEY not found. LLM will not run.")

        genai.configure(api_key=api_key)
        #self.model = genai.GenerativeModel("gemini-1.5-flash")
        self.model = genai.GenerativeModel("gemini-1.5-pro-latest")

    def validate(self, claim, dev_result):

        fraud_score = dev_result.get("fraud_score", 0)
        dev_decision = dev_result.get("decision", "APPROVED")

        prompt = f"""
You are a senior Insurance QA Analyst.

Review the following claim:

Claim Amount: {claim.total_claim_amount}
Premium: {claim.policy_annual_premium}
Age: {claim.insured_age}
Incident Severity: {claim.incident_severity}
Previous Claims: {claim.previous_claims_count}
Hospital Risk: {claim.hospital_risk_score}
Fraud Score: {fraud_score}
Dev Decision: {dev_decision}

Return ONLY valid JSON in this format:

{{
    "status": "APPROVED or REJECTED",
    "risk_level": "LOW or MEDIUM or HIGH",
    "needs_human_approval": true or false,
    "reasoning": "short explanation"
}}

Rules:
- Fraud score > 0.85 → REJECTED
- Fraud score between 0.6–0.85 → needs_human_approval true
- Very high claim ratio → HIGH risk
- Otherwise APPROVED
"""

        try:

            print("\n==============================")
            print("PROMPT SENT TO LLM:")
            print(prompt)
            print("==============================\n")

            print("Calling GenAI LLM for QA validation...")

            # response = self.client.chat.completions.create(
            #     model="gpt-4o-mini",
            #     temperature=0,
            #     response_format={"type": "json_object"},
            #     messages=[
            #         {"role": "system", "content": "You are an insurance QA expert."},
            #         {"role": "user", "content": prompt}
            #     ]
            # )

            response = self.model.generate_content(prompt) #updated for GenAI

            # content = response.choices[0].message.content

            content = response.text #udpated for GenAI

            print("\n==============================")
            print("LLM RAW OUTPUT:")
            print(content)
            print("==============================\n")

            qa_result = json.loads(content.strip())

        except Exception as e:

            print("LLM QA Error:", e)
            print("Using rule-based fallback...")

            # Safe rule-based fallback
            if fraud_score > 0.85:
                qa_result = {
                    "status": "REJECTED",
                    "risk_level": "HIGH",
                    "needs_human_approval": False,
                    "reasoning": "High fraud score detected by fallback rule."
                }

            elif fraud_score > 0.6:
                qa_result = {
                    "status": "PENDING",
                    "risk_level": "MEDIUM",
                    "needs_human_approval": True,
                    "reasoning": "Moderate fraud score requires human review."
                }

            else:
                qa_result = {
                    "status": "APPROVED",
                    "risk_level": "LOW",
                    "needs_human_approval": False,
                    "reasoning": "Low fraud score fallback approval."
                }

        # Final Safety Defaults
        qa_result.setdefault("status", "PENDING")
        qa_result.setdefault("risk_level", "MEDIUM")
        qa_result.setdefault("needs_human_approval", True)
        qa_result.setdefault("reasoning", "QA validation completed")

        print("\nFinal QA Result:", qa_result)

        return qa_result