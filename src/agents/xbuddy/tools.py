"""Agent tools.

Reference: https://github.com/Victoria824/FounderBuddy/blob/main/src/agents/founder_buddy/tools.py

TODO: Implement get_context tool that loads the context packet for a section.
This is called by the router node to get the system prompt and validation
rules for the current section.
"""

from langchain_core.tools import tool

from .enums import SectionID
from .prompts import get_section_template


@tool
async def get_context(
    user_id: int,
    thread_id: str,
    section_id: str,
    user_data: dict | None = None,
) -> dict:
    """Load context packet for a section.

    Returns a dict with: section_id, status, system_prompt, draft, validation_rules.
    The router calls this to get the system prompt for the current section.
    """
    section_enum = SectionID(section_id)
    template = get_section_template(section_enum)

    return {
        "section_id": section_id,
        "status": "in_progress",
        "system_prompt": template.system_prompt_template,
        "draft": None,
        "validation_rules": [r.model_dump() for r in template.validation_rules],
    }
