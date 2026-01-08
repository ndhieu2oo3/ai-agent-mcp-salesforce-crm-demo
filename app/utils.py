import json
import re

def extract_and_parse_json(response_text):
    """Trích xuất và parse JSON từ response của LLM"""
    try:
        # Thử parse trực tiếp
        return json.loads(response_text)
    except json.JSONDecodeError:
        # Tìm JSON trong markdown code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```', 
                              response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Tìm JSON object/array đầu tiên
        json_match = re.search(r'(\{.*\}|\[.*\])', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        raise ValueError("Không tìm thấy JSON hợp lệ trong response")