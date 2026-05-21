"""Generate reply node — calls the LLM to produce a conversational response.

Uses the system prompt from context_packet (loaded by the router) and the
recent conversation history from short_memory to generate the next message.
"""

import logging
from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig

from core.llm import get_model
from ..models import XBuddyState

logger = logging.getLogger(__name__)


async def generate_reply_node(state: XBuddyState, config: RunnableConfig) -> dict:
    """Generate a conversational reply for the current section.

    Builds a prompt from:
    - system_prompt: the section-specific instructions from context_packet
    - short_memory: recent messages (trimmed to avoid token overflow)

    Returns the AI message appended to both `messages` and `short_memory`.
    """
    context_packet = state.get("context_packet")
    if not context_packet:
        raise ValueError("context_packet is missing — router_node must run first")

    system_prompt = context_packet.system_prompt
    short_memory = state.get("short_memory", [])

    # Build the message list: system instructions + recent conversation
    # short_memory already includes the latest HumanMessage from the user
    messages = [SystemMessage(content=system_prompt)] + short_memory

    logger.info(
        f"[generate_reply] section={state.get('current_section').value} "
        f"history_len={len(short_memory)}"
    )

    model = get_model()
    response = await model.ainvoke(messages, config=config)

    # Append the AI response to both conversation lists
    return {
        "messages": [response],
        "short_memory": short_memory + [response],
    }
