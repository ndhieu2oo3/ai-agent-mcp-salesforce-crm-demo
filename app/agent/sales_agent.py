import json
import logging
from app.extensions import config
from app.utils import extract_and_parse_json

class SalesAgent:
    def __init__(self, llm_client, mcp_server, system_prompt):
        self.llm = llm_client
        self.mcp = mcp_server
        self.system_prompt = system_prompt

    def run(self, opp_id: str, meeting_note: str):
        logging.info("Agent started processing meeting note")

        prompt = f"""
Phân tích meeting note sau và TRẢ VỀ JSON HỢP LỆ theo format:

{{
  "summary": "...",
  "next_action": {{
    "action": "...",
    "due_date": "..."
  }},
  "keywords": ["..."],
  "status": "Open | Qualified | Proposal | Closed"
}}

Meeting note:
\"\"\"{meeting_note}\"\"\"
"""

        raw_output = self.llm.chat(
            system_prompt=self.system_prompt,
            user_prompt=prompt,
            temperature=config.LLM_TEMPERATURE
        )

        logging.info("LLM raw output: %s", raw_output)

        try:
            data = json.loads(raw_output)
        except Exception as e:
            logging.error("Failed to parse LLM output as JSON")
            raise e

        # [1] Save meeting summary
        self.mcp.save_meeting_log(opp_id, data["summary"])

        # [2] Create next action
        if data.get("next_action") and data["next_action"].get("action"):
            self.mcp.create_next_action(
                opp_id,
                data["next_action"]["action"],
                data["next_action"].get("due_date", "TBD")
            )

        # [3] Update insights
        if data.get("keywords"):
            self.mcp.update_insight_keywords(opp_id, data["keywords"])

        # [4] Update status
        if data.get("status"):
            self.mcp.update_opportunity_status(opp_id, data["status"])

        logging.info("Agent finished processing")

        return data
