"""StudyMate MCP server. Read-only study planning tools, using stdio."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("StudyMate Tools")


@mcp.tool()
def calculate_study_time(days: int, hours_per_day: float) -> dict:
    """Calculate total available study hours from number of days and daily hours."""
    if not 1 <= days <= 365:
        return {"error": "days must be between 1 and 365"}
    if not 0 < hours_per_day <= 24:
        return {"error": "hours_per_day must be above 0 and at most 24"}
    return {"days": days, "hours_per_day": hours_per_day,
            "total_hours": round(days * hours_per_day, 2)}


@mcp.tool()
def create_study_plan(subjects: list[str], total_hours: float) -> dict:
    """Split available study hours evenly across subjects and return a simple plan."""
    clean = [subject.strip() for subject in subjects if subject.strip()]
    if not clean or len(clean) > 12:
        return {"error": "Provide 1 to 12 non-empty subjects"}
    if len(set(name.casefold() for name in clean)) != len(clean):
        return {"error": "Each subject must be unique"}
    if not 0 < total_hours <= 8760:
        return {"error": "total_hours must be above 0 and at most 8760"}
    # Work in minutes to ensure the distributed time adds up exactly.
    total_minutes = round(total_hours * 60)
    per_subject, extra = divmod(total_minutes, len(clean))
    plan = [{"subject": name, "minutes": per_subject + (index < extra)}
            for index, name in enumerate(clean)]
    return {"total_minutes": total_minutes, "study_plan": plan,
            "note": "Start with the hardest subject and add short breaks."}


@mcp.tool()
def get_study_tip(subject: str) -> dict:
    """Return a practical active-recall study tip for a subject."""
    if not subject.strip() or len(subject) > 100:
        return {"error": "subject must contain 1 to 100 characters"}
    return {"subject": subject.strip(),
            "tip": "Study for 25 minutes, close your notes, then explain the topic from memory. Review missed concepts after a 5-minute break."}


if __name__ == "__main__":
    mcp.run(transport="stdio")
