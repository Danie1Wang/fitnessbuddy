"""Memory updater node — persists section state and manages completion.

Runs after generate_decision on every turn. It:
1. Marks sections as DONE and saves content when the user confirmed satisfaction
2. Saves to Supabase if configured (skips gracefully if not)
3. Checks if all 5 sections are done and sets the final output flag
4. Trims short_memory to keep token count under control
"""

import asyncio
import logging
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig

from ..enums import SectionID, SectionStatus
from ..models import SectionContent, SectionState, XBuddyState

logger = logging.getLogger(__name__)

# Keep only this many recent messages in short_memory to avoid token overflow
SHORT_MEMORY_LIMIT = 12


async def memory_updater_node(state: XBuddyState, config: RunnableConfig) -> dict:
    """Update section state, persist to Supabase, and check if all sections are complete."""
    agent_output = state.get("agent_output")
    current_section = state.get("current_section")
    section_states = dict(state.get("section_states", {}))
    messages = state.get("messages", [])

    # --- 1. Save section content if the user confirmed satisfaction ---
    if agent_output and agent_output.should_save_content:
        # Use the last AI message as the section's saved content (the summary)
        last_ai_content = next(
            (m.content for m in reversed(messages) if isinstance(m, AIMessage)), ""
        )

        section_states[current_section.value] = SectionState(
            section_id=current_section,
            status=SectionStatus.DONE,
            satisfaction_status="satisfied",
            content=SectionContent(
                content={},  # Tiptap JSON — empty for now, plain text is what matters
                plain_text=last_ai_content,
            ),
        )

        logger.info(f"[memory_updater] Section {current_section.value} marked DONE")

        # --- 2. Save to Supabase (skip gracefully if not configured) ---
        await _save_to_supabase(state, current_section.value, last_ai_content)

    # --- 3. Check if all sections are complete ---
    all_done = all(
        section_states.get(s.value) is not None
        and section_states[s.value].status == SectionStatus.DONE
        for s in SectionID
    )

    if all_done:
        logger.info("[memory_updater] All sections complete — flagging for final output")

    # --- 4. Trim short_memory to avoid token overflow ---
    # Keep only the most recent messages — the system prompt provides section context
    short_memory = messages[-SHORT_MEMORY_LIMIT:]

    return {
        "section_states": section_states,
        "should_generate_final_output": all_done,
        "short_memory": short_memory,
    }


async def _save_to_supabase(state: XBuddyState, section_id: str, plain_text: str) -> None:
    """Save section content to Supabase. Skips silently if Supabase is not configured."""
    try:
        from integrations.supabase.supabase_client import SupabaseClient
        supabase = SupabaseClient()

        # Supabase client is synchronous — run in executor to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: supabase.save_section_state(
                user_id=state.get("user_id", 1),
                thread_id=state.get("thread_id", ""),
                section_id=section_id,
                content={},
                plain_text=plain_text,
                status="done",
                satisfaction_status="satisfied",
                agent_id="xbuddy",
            ),
        )
        logger.info(f"[memory_updater] Saved section {section_id} to Supabase")

    except (ImportError, ValueError):
        # Supabase not configured — this is fine for local development
        logger.debug(f"[memory_updater] Supabase not configured, skipping save for {section_id}")
    except Exception as e:
        # Log but don't crash — Supabase failure shouldn't stop the conversation
        logger.warning(f"[memory_updater] Supabase save failed for {section_id}: {e}")
