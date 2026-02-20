# agents/human_agent.py

class HumanAgent:
    def requires_human_approval(self, dev_result, qa_result):
        if not qa_result["qa_passed"]:
            return True

        if dev_result["decision"] == "REVIEW":
            return True

        return False

    def final_decision(self, admin_action):
        """
        admin_action: APPROVE | REJECT
        """
        return {
            "final_decision": admin_action,
            "agent": "HUMAN_AGENT"
        }
