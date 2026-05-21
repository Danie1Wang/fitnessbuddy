"""Initialize node — validates and sets up conversation state.

Runs at the start of every graph invocation (every user message).
Ensures state always has valid defaults before any other node runs.
"""

import logging
import uuid
from langchain_core.runnables import RunnableConfig

from ..enums import RouterDirective, SectionID
from ..models import XBuddyData, XBuddyState

logger = logging.getLogger(__name__)


async def initialize_node(state: XBuddyState, config: RunnableConfig) -> dict:
    """Initialize conversation state.

    Reads user_id and thread_id from the request config (set by the API layer).
    Only sets defaults for fields that aren't already set — this node runs on
    every turn so we must not overwrite existing conversation progress.
    """
    configurable = config.get("configurable", {})
    updates = {}

    # Set user identity from the request config if not already in state
    if not state.get("user_id"):
        updates["user_id"] = configurable.get("user_id", 1)

    if not state.get("thread_id"):
        updates["thread_id"] = configurable.get("thread_id", str(uuid.uuid4()))

    # Set starting section for a brand new conversation
    if not state.get("current_section"):
        updates["current_section"] = SectionID.GOALS

    # On a fresh conversation, default to STAY so the router loads GOALS first.
    # NEXT is only set by generate_decision when the user confirms a section is done.
    if not state.get("router_directive"):
        updates["router_directive"] = RouterDirective.STAY

    # Initialize the domain data container if missing
    if not state.get("user_data"):
        updates["user_data"] = XBuddyData()

    # Sync short_memory with the latest messages.
    # short_memory is the trimmed window passed to the LLM — it must include
    # the most recent HumanMessage so generate_reply can see what the user said.
    SHORT_MEMORY_LIMIT = 12
    current_messages = state.get("messages", [])
    current_short_memory = state.get("short_memory", [])
    if current_messages and (
        not current_short_memory
        or current_messages[-1] not in current_short_memory
    ):
        updates["short_memory"] = current_messages[-SHORT_MEMORY_LIMIT:]

    logger.info(
        f"[initialize] user_id={state.get('user_id') or updates.get('user_id')} "
        f"section={state.get('current_section') or updates.get('current_section')}"
    )

    return updates
