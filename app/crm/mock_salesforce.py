from datetime import datetime

class MockSalesforceCRM:
    def __init__(self):
        self.opportunities = {}
        self.tasks = {}
        self.contacts = {}

    def create_opportunity(self, opp_id, name, status="Open"):
        self.opportunities[opp_id] = {
            "id": opp_id,
            "name": name,
            "status": status,
            "meeting_logs": [],
            "insights": [],
            "tasks": []
        }

    def save_meeting_log(self, opp_id, summary):
        self.opportunities[opp_id]["meeting_logs"].append({
            "summary": summary,
            "timestamp": datetime.now()
        })

    def create_task(self, opp_id, action, due_date):
        task = {
            "action": action,
            "due_date": due_date
        }
        self.opportunities[opp_id]["tasks"].append(task)

    def update_insights(self, opp_id, keywords):
        self.opportunities[opp_id]["insights"].extend(keywords)

    def update_status(self, opp_id, status):
        self.opportunities[opp_id]["status"] = status

    def query_history(self, opp_id):
        return self.opportunities[opp_id]
