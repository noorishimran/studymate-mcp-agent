"""Offline MCP client: proves discovery and a two-tool workflow without an LLM."""

import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    server = StdioServerParameters(command=sys.executable,
                                   args=[str(Path(__file__).with_name("server.py"))])
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("CONNECTED TO MCP SERVER: StudyMate Tools")
            print("AVAILABLE MCP TOOLS:")
            for tool in tools.tools:
                print(" -", tool.name, "|", tool.description)

            async def call(name, arguments):
                print(f"\nCALLING MCP TOOL: {name} {json.dumps(arguments)}")
                result = await session.call_tool(name, arguments)
                if result.isError:
                    raise RuntimeError(f"MCP tool {name} failed: {result.content}")
                value = result.structuredContent
                if value is None:
                    value = json.loads(result.content[0].text)
                print("TOOL RESULT:", json.dumps(value, indent=2))
                return value

            time = await call("calculate_study_time", {"days": 5, "hours_per_day": 2})
            # This is a deliberately scripted demo, not AI tool selection.
            plan = await call("create_study_plan", {
                "subjects": ["Python", "MCP", "AI Agents"],
                "total_hours": time["total_hours"],
            })
            tip = await call("get_study_tip", {"subject": "MCP"})
            print("\nFINAL DEMO RESPONSE:")
            print(f"You have {time['total_hours']} study hours across 5 days.")
            for entry in plan["study_plan"]:
                print(f" - {entry['subject']}: {entry['minutes']} minutes")
            print("Tip:", tip["tip"])


if __name__ == "__main__":
    asyncio.run(main())
