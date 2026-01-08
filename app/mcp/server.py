class MCPServer:
    def __init__(self, crm):
        self.crm = crm
    
    def register_agent(self, agent_name, agent):
        self.agent_name = agent_name
        self.agent = agent

    def save_meeting_log(self, opp_id, summary):
        self.crm.save_meeting_log(opp_id, summary)
        return "Meeting log saved"

    def create_next_action(self, opp_id, action, due_date):
        self.crm.create_task(opp_id, action, due_date)
        return "Task created"

    def update_insight_keywords(self, opp_id, keywords):
        self.crm.update_insights(opp_id, keywords)
        return "Insights updated"

    def update_opportunity_status(self, opp_id, status):
        self.crm.update_status(opp_id, status)
        return "Opportunity status updated"

    def query_opportunity_history(self, opp_id):
        # Return a JSON-serializable copy (convert datetimes to ISO strings)
        raw = self.crm.query_history(opp_id)

        def serialize(obj):
            from datetime import datetime

            if isinstance(obj, dict):
                return {k: serialize(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [serialize(v) for v in obj]
            if isinstance(obj, datetime):
                return obj.isoformat()
            return obj

        return serialize(raw)
