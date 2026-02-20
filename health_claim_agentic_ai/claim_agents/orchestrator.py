from claim_agents.dev_agent import DevAgent
from claim_agents.qa_agent import QAAgent
from claim_agents.qa_agent_llm import QAAgentLLM
from claim_agents.human_agent import HumanAgent
import inspect

class Orchestrator:
    print("DevAgent loaded from:", inspect.getfile(DevAgent))
    def __init__(self, use_llm_qa=True):
        self.dev_agent = DevAgent()
        self.rule_qa = QAAgent()
        self.llm_qa = QAAgentLLM()
        self.human_agent = HumanAgent()
        self.use_llm_qa = use_llm_qa

    def process_claim(self, claim):
        # ML Fraud Detection
        dev_result = self.dev_agent.evaluate_claim(claim)

        # QA Layer
        if self.use_llm_qa:
            qa_result = self.llm_qa.validate(claim, dev_result)
        else:
            qa_result = self.rule_qa.validate(claim, dev_result)

        #  Human-in-the-loop decision
        needs_human = (
            qa_result.get("needs_human_approval", False)
            or dev_result["decision"] == "REVIEW"
        )

        return {
            "dev_result": dev_result,
            "qa_result": qa_result,
            "needs_human_approval": needs_human,
            "status": "PENDING_ADMIN" if needs_human else dev_result["decision"]
        }
