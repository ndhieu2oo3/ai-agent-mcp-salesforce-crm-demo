import re

def strip_json_mark(text: str) -> str:
    """
    Remove ```json / ``` wrappers from LLM output if present
    and return clean JSON string.
    """

    if not text:
        return text

    text = text.strip()

    # Case 1: ```json ... ```
    fence_pattern = re.compile(
        r"```(?:json)?\s*(.*?)\s*```",
        re.DOTALL | re.IGNORECASE
    )

    match = fence_pattern.search(text)
    if match:
        return match.group(1).strip()

    # Case 2: raw JSON already
    if text.startswith("{") and text.endswith("}"):
        return text

    return text