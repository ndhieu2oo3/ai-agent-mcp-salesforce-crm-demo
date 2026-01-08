from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from datetime import datetime
from pathlib import Path
import logging
import uvicorn

from app.agent.llm_client import LLMClient
from app.agent.sales_agent import SalesAgent
from app.crm.mock_salesforce import MockSalesforceCRM
from app.mcp.server import MCPServer
from app.extensions import config

app = FastAPI(title="AI Sales Agent Demo")

# ==== INIT SYSTEM ====
logging.info("Initializing system...")

crm = MockSalesforceCRM()
crm.create_opportunity("OPP001", "ABC Corp")

mcp = MCPServer(crm)

llm_client = LLMClient(
    base_url=config.LLM_DOMAIN,
    model=config.LLM_MODEL_NAME
)

agent = SalesAgent(
    llm_client=llm_client,
    mcp_server=mcp,
    system_prompt=config.SYSTEM_PROMPT
)

logging.info("System ready")
logging.info("LLM Model: %s", config.LLM_MODEL_NAME)
logging.info("LLM Endpoint: %s", config.LLM_DOMAIN)

# ==== ROUTES ====

@app.get("/", response_class=HTMLResponse)
def chat_ui():
    # Resolve chat.html relative to the repository root (two levels up from this file)
    try:
        base = Path(__file__).resolve().parents[1]
        html_path = base.joinpath("chat.html")
        text = html_path.read_text(encoding="utf-8")
        return HTMLResponse(content=text)
    except Exception as e:
        logging.exception("Failed to load chat.html")
        return HTMLResponse(content="<h1>Error loading UI</h1><pre>" + str(e) + "</pre>", status_code=500)


@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    meeting_note = body.get("message")

    if not meeting_note:
        return JSONResponse({"error": "Empty message"}, status_code=400)

    try:
        result = agent.run("OPP001", meeting_note)
    except Exception as e:
        logging.exception("Agent run failed")
        return JSONResponse({"error": "Agent execution failed", "detail": str(e)}, status_code=500)

    try:
        crm_state = mcp.query_opportunity_history("OPP001")
    except Exception:
        logging.exception("Failed to query CRM state")
        crm_state = {}

    return JSONResponse({"agent_result": result, "crm_state": crm_state})


@app.get("/system")
def system_info():
    return {
        "time": datetime.now().isoformat(),
        "llm_model": config.LLM_MODEL_NAME,
        "llm_domain": config.LLM_DOMAIN,
        "opportunities": list(crm.opportunities.keys())
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",   
        port=8000,
        reload=False
    )