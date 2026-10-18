"""Gemini agent that discovers and executes tools via an actual MCP client."""

import asyncio
import json
import os
import sys
import traceback
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    load_dotenv(Path(__file__).with_name(".env"))
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise SystemExit("GEMINI_API_KEY missing. Add your own key to a .env file next to agent.py")

    prompt = " ".join(sys.argv[1:]) or (
        "I have 5 days and 2 hours per day. Plan study time for Python, MCP, "
        "and AI Agents, and give me one MCP study tip."
    )
    params = StdioServerParameters(command=sys.executable,
                                   args=[str(Path(__file__).with_name("server.py"))])
    client = genai.Client(api_key=api_key)
    try:
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as mcp:
                await mcp.initialize()
                discovered = (await mcp.list_tools()).tools
                available = {tool.name for tool in discovered}
                declarations = [types.FunctionDeclaration(
                    name=tool.name,
                    description=tool.description or tool.name,
                    parameters_json_schema=tool.inputSchema,
                ) for tool in discovered]
                print("GEMINI AI AGENT CONNECTED TO MCP SERVER: StudyMate Tools")
                print("AVAILABLE MCP TOOLS:", ", ".join(sorted(available)))
                print("USER REQUEST:", prompt)

                contents = [types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]
                config = types.GenerateContentConfig(
                    system_instruction=(
                        "You are StudyMate. Use MCP tools for calculations and plans. "
                        "For a study plan calculate the total time first, then feed "
                        "that total into create_study_plan. If a study tip is requested, "
                        "call get_study_tip. Explain errors; never invent tool results."
                    ),
                    tools=[types.Tool(function_declarations=declarations)],
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
                )
                for _ in range(8):
                    print("\nContacting Gemini API...", flush=True)
                    response = await client.aio.models.generate_content(
                        model=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
                        contents=contents, config=config,
                    )
                    calls = response.function_calls or []
                    if not calls:
                        print("\nFINAL AI RESPONSE:\n", response.text or "No text response was returned.")
                        return

                    contents.append(response.candidates[0].content)
                    results = []
                    for call in calls:
                        name = call.name or ""
                        arguments = dict(call.args or {})
                        print(f"\nAI SELECTED MCP TOOL: {name} {json.dumps(arguments)}")
                        if name not in available:
                            data = {"error": f"Unknown MCP tool: {name}"}
                        else:
                            try:
                                result = await mcp.call_tool(name, arguments)
                                if result.isError:
                                    data = {"error": str(result.content)}
                                elif result.structuredContent is not None:
                                    data = result.structuredContent
                                else:
                                    data = json.loads(result.content[0].text)
                            except Exception as exc:
                                data = {"error": str(exc)}
                        print("MCP TOOL RESULT:", json.dumps(data, ensure_ascii=False))
                        results.append(types.Part.from_function_response(
                            name=name, response=data,
                        ))
                    # Gemini GenerateContent expects tool results as a user turn.
                    contents.append(types.Content(role="user", parts=results))
                raise RuntimeError("Agent reached the 8-round tool-call safety limit")
    except Exception as exc:
        print("\nDETAILED AGENT ERROR (share this text, but never your API key):", file=sys.stderr)
        traceback.print_exception(exc, file=sys.stderr)
        raise SystemExit(1) from None
    finally:
        await client.aio.aclose()


if __name__ == "__main__":
    asyncio.run(main())
