import json
import logging
from typing import Dict
from app.extensions import config
from app.utils import strip_json_mark


class SalesAgent:
    def __init__(self, llm_client, mcp_server, system_prompt):
        self.llm = llm_client
        self.mcp = mcp_server
        self.system_prompt = system_prompt

    # =====================================================
    # PUBLIC ENTRY
    # =====================================================
    def run(self, meeting_note: str) -> Dict:
        logging.info("Agent received input")

        intent = self._detect_intent(meeting_note)
        logging.info("Detected intent: %s", intent)

        if intent == "MEETING_NOTE":
            return self._handle_meeting_note(meeting_note)

        if intent == "QUERY_LAST_MEETING":
            return self._handle_query_last_meeting()

        if intent == "QUERY_TASKS":
            return self._handle_query_tasks()

        if intent == "QUERY_OVERVIEW":
            return self._handle_query_overview()

        return {"reply": "Xin lỗi, tôi chưa hiểu yêu cầu của bạn."}

    # =====================================================
    # INTENT DETECTION
    # =====================================================
    def _detect_intent(self, text: str) -> str:
        prompt = f"""
Phân loại input sau thành đúng 1 trong các intent sau:

- MEETING_NOTE
- QUERY_LAST_MEETING
- QUERY_TASKS
- QUERY_OVERVIEW

Chỉ trả về đúng TÊN INTENT.

Input:
\"\"\"{text}\"\"\"
"""
        result = self.llm.chat(
            system_prompt="You are an intent classifier",
            user_prompt=prompt,
            temperature=0
        ).strip()

        return result

    # =====================================================
    # MEETING NOTE HANDLER
    # =====================================================
    def _handle_meeting_note(self, meeting_note: str) -> Dict:
        prompt = f"""
Phân tích meeting note sau và TRẢ VỀ JSON HỢP LỆ theo format:

{{
  "company": "...",
  "summary": "...",
  "next_action": {{
    "action": "...",
    "due_date": "YYYY-MM-DD | TBD"
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
            data = json.loads(strip_json_mark(raw_output))
        except Exception:
            raise ValueError("LLM did not return valid JSON")

        # ---- resolve opportunity ----
        company = data.get("company", "Unknown")
        opp_id = f"OPP_{company.upper()}"

        if opp_id not in self.mcp.crm.opportunities:
            self.mcp.crm.create_opportunity(opp_id, company)

        # ---- MCP tool calls ----
        self.mcp.save_meeting_log(opp_id, data["summary"])

        if data.get("next_action") and data["next_action"].get("action"):
            self.mcp.create_next_action(
                opp_id,
                data["next_action"]["action"],
                data["next_action"].get("due_date", "TBD")
            )

        if data.get("keywords"):
            self.mcp.update_insight_keywords(opp_id, data["keywords"])

        if data.get("status"):
            self.mcp.update_opportunity_status(opp_id, data["status"])

        return {
            "reply": f"Đã cập nhật thông tin cho deal {company}.",
            "opp_id": opp_id
        }

    # =====================================================
    # QUERY HANDLERS (NO LLM)
    # =====================================================
    def _handle_query_last_meeting(self) -> Dict:
        opp = self._get_latest_opp()
        meetings = opp.get("meeting_logs", [])

        if not meetings:
            return {"reply": "Deal này chưa có cuộc họp nào."}

        last = meetings[-1]
        return {"reply": last["summary"]}

    def _handle_query_tasks(self) -> Dict:
        opp = self._get_latest_opp()
        tasks = opp.get("tasks", [])

        if not tasks:
            return {"reply": "Hiện tại chưa có task nào."}

        lines = [
            f"- {t['action']} (Due: {t['due_date']})"
            for t in tasks
        ]
        return {"reply": "Các task hiện tại:\n" + "\n".join(lines)}

    def _handle_query_overview(self) -> Dict:
        opp = self._get_latest_opp()

        return {
            "reply": (
                f"Deal {opp['name']} đang ở trạng thái {opp['status']}.\n"
                f"Số cuộc họp: {len(opp['meeting_logs'])}\n"
                f"Số task: {len(opp['tasks'])}"
            )
        }

    # =====================================================
    # UTIL
    # =====================================================
    def _get_latest_opp(self) -> Dict:
        if not self.mcp.crm.opportunities:
            raise ValueError("No opportunity found")

        # lấy opp mới nhất (demo đơn giản)
        return list(self.mcp.crm.opportunities.values())[-1]
