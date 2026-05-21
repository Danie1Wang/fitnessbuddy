"""Router node — handles section navigation and context loading.

Reads the router_directive set by the previous turn's generate_decision node,
advances the section if needed, then loads the system prompt for the current section
into context_packet so generate_reply knows what to say.
"""

import logging
from langchain_core.runnables import RunnableConfig

from ..enums import RouterDirective, SectionID, SectionStatus
from ..models import ContextPacket, SectionState, XBuddyState
from ..prompts import get_next_section, get_section_template

logger = logging.getLogger(__name__)


async def router_node(state: XBuddyState, config: RunnableConfig) -> dict:
    """Route to the correct section and load its context packet."""
    directive = state.get("router_directive", RouterDirective.NEXT)
    current = state.get("current_section", SectionID.GOALS)
    section_states = dict(state.get("section_states", {}))

    # --- Navigation logic ---
    if directive == RouterDirective.NEXT or directive == "next":
        # Advance to the next section in sequence
        next_sec = get_next_section(current)
        if next_sec:
            current = next_sec
            logger.info(f"[router] Advancing to section: {current.value}")
        else:
            # No next section — all done, signal completion
            logger.info("[router] All sections complete")
            return {
                "current_section": current,
                "should_generate_final_output": True,
                "router_directive": RouterDirective.STAY,
            }

    elif isinstance(directive, str) and directive.startswith("modify:"):
        # Jump to a specific section (user wants to revisit)
        section_id_str = directive.split(":", 1)[1]
        try:
            current = SectionID(section_id_str)
            logger.info(f"[router] Jumping to section: {current.value}")
        except ValueError:
            logger.warning(f"[router] Unknown section in modify directive: {section_id_str}")

    else:
        # RouterDirective.STAY — stay on the current section
        logger.info(f"[router] Staying on section: {current.value}")

    # --- Load context for current section ---
    template = get_section_template(current)
    context_packet = ContextPacket(
        section_id=current,
        status=SectionStatus.IN_PROGRESS,
        system_prompt=template.system_prompt_template,
    )

    # Mark the section as in-progress if it hasn't been started yet
    if current.value not in section_states:
        section_states[current.value] = SectionState(
            section_id=current,
            status=SectionStatus.IN_PROGRESS,
        )

    return {
        "current_section": current,
        "context_packet": context_packet,
        "section_states": section_states,
        "router_directive": RouterDirective.STAY,  # Reset after processing
    }
