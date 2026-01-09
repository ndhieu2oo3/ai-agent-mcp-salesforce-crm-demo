# AI Sales Agent Demo

A FastAPI-based AI agent system that analyzes sales meeting notes and automatically updates CRM records using a local Qwen3 LLM.

## What It Does

- **Meeting Analysis**: Submit meeting notes via web UI
- **AI Processing**: Qwen3-4B LLM extracts key insights (summary, next actions, keywords, opportunity status)
- **CRM Integration**: Automatically saves results to a mock Salesforce CRM
- **Live Feedback**: View CRM changes in real-time on the dashboard

## Architecture

```
Frontend (chat.html)
        ↓ POST /chat
      ↓
FastAPI Backend (app/main.py)
        ↓
    SalesAgent (app/agent/sales_agent.py)
        ↓
   LLMClient (app/agent/llm_client.py) → vLLM Server (port 8001)
        ↓
   MCPServer (app/mcp/server.py)
        ↓
   MockSalesforceCRM (app/crm/mock_salesforce.py)
```

### Backend Flow

1. **User Input**: Meeting note submitted via web form
2. **LLM Processing**: 
   - Prompt sent to Qwen3-4B via vLLM API
   - LLM returns JSON with: `summary`, `next_action`, `keywords`, `status`
3. **CRM Updates**:
   - Save meeting log with timestamp
   - Create task if action suggested
   - Add insight keywords
   - Update opportunity status
4. **Response**: Return agent analysis + updated CRM state to UI

## Quick Start

### Prerequisites
- Python 3.10+
- Conda
- GPU (CUDA 12+) for vLLM
- ≥8GB VRAM

### Setup & Run

```bash
# One command to start everything
bash run.sh
```

The script will:
1. Create/activate conda environment
2. Install dependencies
3. Start vLLM server (port 8001)
4. Start FastAPI app (port 8000)

### Manual Start (if needed)

**Terminal 1 - vLLM Server:**
```bash
CUDA_VISIBLE_DEVICES=1 python -m vllm.entrypoints.openai.api_server \
  --model ./model/Qwen3-4B-Instruct-2507 \
  --served-model-name Qwen3-4B-Instruct-2507 \
  --port 8001 \
  --gpu-memory-utilization 0.8
```

**Terminal 2 - Agent App:**
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Access
- **UI**: http://localhost:8000
- **System Status**: http://localhost:8000/system

## Project Structure

```
app/
├── main.py              # FastAPI routes & initialization
├── extensions.py        # Config loader (.env)
├── utils.py             # Helper functions (JSON parsing)
├── agent/
│   ├── sales_agent.py   # Core agent logic (prompt, parsing, CRM calls)
│   └── llm_client.py    # LLM API wrapper (HTTP to vLLM)
├── crm/
│   └── mock_salesforce.py # Fake Salesforce CRM storage
└── mcp/
    └── server.py        # MCP interface (agent ↔ CRM bridge)

chat.html               # Web UI
.env                    # Config (LLM_DOMAIN, MODEL_NAME, etc.)
requirements.txt        # Python dependencies
```

## Configuration

Edit `.env` to customize:

```env
DEVICE=1                                    # GPU device ID
LLM_MODEL_NAME=Qwen3-4B-Instruct-2507      # Model name
LLM_DOMAIN=http://localhost:8001           # vLLM server URL
LLM_TEMPERATURE=0.8                        # LLM creativity (0-1)
SYSTEM_PROMPT=Bạn là AI Sales Assistant... # Agent system prompt
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web UI (HTML) |
| `/chat` | POST | Process meeting note |
| `/system` | GET | System info & status |

### POST /chat

**Request:**
```json
{
  "message": "Khách hàng muốn demo về bảo mật. Ngân sách 50k."
}
```

**Response:**
```json
{
  "agent_result": {
    "summary": "...",
    "next_action": { "action": "...", "due_date": "..." },
    "keywords": ["..."],
    "status": "Qualified"
  },
  "crm_state": {
    "id": "OPP001",
    "name": "ABC Corp",
    "status": "Qualified",
    "meeting_logs": [...],
    "tasks": [...],
    "insights": [...]
  }
}
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Blank UI | Check logs: `cat log/vllm.log` |
| LLM not found | Ensure `./model/Qwen3-4B-Instruct-2507` exists |
| Port 8001/8000 in use | Change ports in `.env` and `run.sh` |
| vLLM import error (flash_attn) | Rebuild: `pip install flash-attn==2.5.9` |

## Development Notes

- Agent uses streaming LLM client with timeout=120s
- JSON parsing extracts first valid JSON from LLM output (handles markdown code blocks)
- CRM is in-memory; data lost on restart
- Uses Vietnamese prompts (can be changed in SYSTEM_PROMPT)

## Future Improvements

- [ ] Persistent database (PostgreSQL)
- [ ] Multi-agent orchestration
- [ ] Async processing with task queue
- [ ] WebSocket for live updates
- [ ] Docker Compose for full stack

---

**Language**: Vietnamese/English  
**Model**: Qwen3-4B-Instruct-2507 (local)  
**Framework**: FastAPI + vLLM
