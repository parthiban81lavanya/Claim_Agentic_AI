from claim_agents.dev_agent import DevAgent
from claim_agents.qa_agent import QAAgent
from claim_agents.qa_agent_llm import QAAgentLLM
from claim_agents.human_agent import HumanAgent
from claim_agents.audit_agent import AuditAgent
import inspect


class Orchestrator:

    print("DevAgent loaded from:", inspect.getfile(DevAgent))

    def __init__(self, use_llm_qa=False):
        self.dev_agent = DevAgent()
        
        self.rule_qa = QAAgent()
        print("QAAgent loaded")
        
        self.llm_qa = QAAgentLLM()
        print("QA_llm_Agent loaded")
        
        self.human_agent = HumanAgent()
        print("human agent loaded")
        
        #self.audit_agent = AuditAgent()
        print("audit agent loaded")

        self.use_llm_qa = use_llm_qa

    # ====================================================
    # 🤖 MAIN AI PIPELINE
    # ====================================================
    def process_claim(self, claim):

        # -----------------------------------
        # Dev Agent (ML Layer)
        # -----------------------------------
        dev_result = self.dev_agent.evaluate_claim(claim)

        dev_decision = dev_result.get("decision", "APPROVED")
        fraud_score = dev_result.get("fraud_score", 0)

        # -----------------------------------
        # QA Agent (Rule or LLM)
        # -----------------------------------
        if self.use_llm_qa:
            qa_result = self.llm_qa.validate(claim, dev_result)
            print("QA Result from LLM agent")
        else:
            qa_result = self.rule_qa.validate(claim, dev_result)
            print("QA Result from qa agent")

        # Normalize QA output (safe defaults)
        qa_result.setdefault("status", "APPROVED")
        qa_result.setdefault("needs_human_approval", False)
        qa_result.setdefault("risk_level", "LOW")
        qa_result.setdefault("reasoning", "")

        qa_status = qa_result["status"]
        risk_level = qa_result["risk_level"]
        needs_human_flag = qa_result["needs_human_approval"]
        qa_reasoning = qa_result["reasoning"]

        # -----------------------------------
        # FINAL DECISION ENGINE
        # -----------------------------------

        # Immediate Reject from dev or QA
        if  qa_status == "REJECTED" or risk_level == "HIGH":
            final_status = "REJECTED"
            reject_reason = qa_reasoning

        # Needs Human Review
        elif needs_human_flag or dev_decision == "REVIEW" :
            final_status = "PENDING_HUMAN_REVIEW"
            reject_reason = qa_reasoning

        # Auto Approved
        else:
            final_status = "APPROVED"
            reject_reason = None
            
        decision_agent = "RULE_QA_AGENT" if not self.use_llm_qa else "QA_LLM_AGENT"

        self.audit_agent.log_decision(
            claim,
            dev_result,
            qa_result,
            final_status,
            decision_agent
        )
        # -----------------------------------
        # FINAL RETURN (NO HUMAN EXECUTION HERE)
        # -----------------------------------
        return {
            "dev_result": dev_result,
            "qa_result": qa_result,
            "status": final_status,
            "risk_level": risk_level,
            "fraud_score": fraud_score,
            "reject_reason": reject_reason,
            "needs_human": final_status == "PENDING_HUMAN_REVIEW"
        }

    # ====================================================
    #  HUMAN REVIEW ENTRY POINT
    # ====================================================
    def process_human_review(self, claim, manual_decision, reviewer_name):

        human_result = self.human_agent.review(
            claim,
            manual_decision,
            reviewer_name
        )

        return human_result