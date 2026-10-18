# StudyMate: My First MCP-Powered AI Agent

A beginner-friendly Python project that demonstrates how an AI agent connects to a custom **Model Context Protocol (MCP)** server and uses its tools for student study planning.

## Architecture

`User → Gemini model (agent.py) → MCP client (Python SDK) → stdio → MCP server (server.py) → custom tools → Gemini's final response`

- **AI model:** understands natural language and decides which tool(s) to call.
- **MCP client:** discovers available tools and sends structured tool calls.
- **MCP server:** exposes validated tool interfaces using the official Python MCP SDK.
- **Tools:** Python functions that return JSON-like dictionaries.

MCP is a standardized way to expose tools and context across applications. **Function calling** is how a particular model asks to invoke functions; **MCP** standardizes how a client discovers tools and communicates with a separate server. They can work together.

## Three custom tools

| Tool | Input | Output |
|---|---|---|
| `calculate_study_time` | `days: int`, `hours_per_day: float` | Total hours or validation error |
| `create_study_plan` | `subjects: list[str]`, `total_hours: float` | Minutes per subject or validation error |
| `get_study_tip` | `subject: str` | Active-recall recommendation or validation error |

## Setup (Windows / VS Code)

Install **Python 3.11+** and open this folder in VS Code. In the VS Code terminal:

```powershell
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

On macOS/Linux use `python3 -m venv .venv` and `source .venv/bin/activate`.

## Run the no-key MCP test first

```powershell
python demo.py
```

This starts the **real MCP server as a child process**, discovers all tools over stdio, invokes three tools in sequence and prints each input/output plus a final study plan. The calls in `demo.py` are **scripted**, so this step verifies the MCP connection but does **not** demonstrate model-based tool selection.

## Run the real AI agent

Create a file named `.env` in the project folder by copying `.env.example`. Replace `your_gemini_api_key_here` with **your own Gemini API key**, created at [Google AI Studio](https://aistudio.google.com/apikey). Check current free-tier limits and pricing before use. Never share or commit `.env`.

```powershell
python agent.py
```

Or ask a custom question:

```powershell
python agent.py "I have 4 days, 3 hours daily. Plan Python and databases and give me a Python tip."
```

The **Gemini model** interprets the request. Our Python MCP client discovers the actual server tool schemas and sends them to Gemini. Gemini selects a function; the client forwards its arguments through MCP, returns the result to Gemini, and repeats until it produces an answer. `AI SELECTED MCP TOOL` and `MCP TOOL RESULT` make tool calls visible. Actual wording and exact selection may vary between model runs.

**Note:** Do not run `server.py` directly for screenshots: stdio servers normally wait silently for a client's requests. `demo.py` or `agent.py` shows the connection status.

## Multi-step workflow

1. Student asks for a study plan (5 days, 2 hours/day, Python/MCP/AI Agents).
2. Agent invokes `calculate_study_time(5, 2)` → **10 hours**.
3. Agent invokes `create_study_plan(["Python", "MCP", "AI Agents"], 10)` → **200, 200, 200 minutes**.
4. Agent invokes `get_study_tip("MCP")` → active recall tip.
5. Agent combines the results in a friendly final response.

## Errors and safety

- Server validates ranges, blank subjects and duplicate subjects.
- No file deletion, shell execution, outside API connections, or private data access is offered by the MCP tools.
- API key stays in the ignored `.env` file.
- The agent displays tool errors rather than silently guessing.
- Connect only to trusted MCP servers; ask for explicit user confirmation before adding tools that modify data.

## Assignment screenshots checklist

Take genuine screenshots on your own computer; do not fabricate tool call screenshots.

1. **Server running / connection:** `python demo.py` showing `CONNECTED TO MCP SERVER`.
2. **Available tools:** Same terminal showing `AVAILABLE MCP TOOLS` and three names.
3. **AI agent connected:** `python agent.py` showing `GEMINI AI AGENT CONNECTED TO MCP SERVER` (requires real key).
4. **Successful tool call:** Demo terminal showing `CALLING MCP TOOL` and `TOOL RESULT`.
5. **Multi-tool workflow:** Demo with all three tool calls; for real LLM tool choice show `AI SELECTED MCP TOOL` lines.
6. **Final result:** Terminal showing `FINAL AI RESPONSE` (or `FINAL DEMO RESPONSE` clearly labeled as offline test).

Suggested GitHub repository: `studymate-mcp-agent`. Push `server.py`, `agent.py`, `demo.py`, `README.md`, `requirements.txt`, `.env.example`, and `.gitignore`. **Never push `.env` or your API key.**

## Simple explanation for teacher

"MCP is a standard bridge between an AI application and external tools. I built a Python MCP server with three tools for student study planning. The agent connects through an MCP client using stdio, discovers the tools, calls the relevant ones, receives structured results, and returns a study plan. My project demonstrates multi-tool chaining and input validation."

## References

- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Gemini Python SDK and function calling](https://googleapis.github.io/python-genai/)
