"""Implementation node — synthesizes all section data into a training program.

Runs once when all 5 sections are complete. Collects the plain_text summary
from each section, feeds it into a comprehensive prompt, and generates a
structured weekly training program. Saves to Supabase and marks the conversation done.
"""

import asyncio
import logging
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig

from core.llm import get_model
from ..enums import SectionID
from ..models import XBuddyState

logger = logging.getLogger(__name__)

SYNTHESIS_PROMPT = """You are an expert fitness coach. Based on the following information
collected from a client, create a comprehensive, personalised training program.

{section_summaries}

---

Create a structured 12-week training program that includes:

## 1. Program Overview
- Summary of the client's goals and constraints
- Overall approach and philosophy for this specific person

## 2. Weekly Training Schedule
- A clear week structure showing which days to train and which to rest
- Each training day should specify: focus area, duration, intensity level

## 3. Workout Details
For each type of workout in the schedule, provide:
- Specific exercises with sets and reps (or time for cardio)
- Brief notes on form or progression
- Modifications for any mentioned injuries or limitations

## 4. Nutrition Guidelines
- Key principles aligned with their goal (deficit/surplus/maintenance)
- Simple daily targets (protein, rough calories if appropriate)
- Practical meal timing tips

## 5. Recovery & Lifestyle Tips
- Sleep and stress management advice tailored to their situation
- Signs of overtraining to watch for
- How to adjust if life gets busy

## 6. 4-Week Milestones
- What they should expect after week 4, 8, and 12
- How to measure progress beyond the scale

Write in a warm, direct coaching tone. Be specific — no vague advice.
"""


async def implementation_node(state: XBuddyState, config: RunnableConfig) -> dict:
    """Generate the personalised FitnessBuddy training program."""
    section_states = state.get("section_states", {})

    # Collect the plain text summary from each completed section
    section_summaries = []
    for section in SectionID:
        section_state = section_states.get(section.value)
        if section_state and section_state.content and section_state.content.plain_text:
            section_summaries.append(
                f"### {section.value.upper()}\n{section_state.content.plain_text}"
            )

    if not section_summaries:
        logger.warning("[implementation] No section content found — generating with minimal data")

    summaries_text = "\n\n".join(section_summaries) if section_summaries else "No section data collected."
    full_prompt = SYNTHESIS_PROMPT.format(section_summaries=summaries_text)

    logger.info(f"[implementation] Generating training program for user {state.get('user_id')}")

    model = get_model()
    response = await model.ainvoke(
        [HumanMessage(content=full_prompt)],
        config=config,
    )
    final_output = response.content

    logger.info(f"[implementation] Program generated ({len(final_output)} chars)")

    # Save to Supabase
    await _save_final_output(state, final_output)

    # Deliver the program to the user as the final message
    delivery_message = AIMessage(
        content=(
            "Your personalised training program is ready! Here it is:\n\n"
            + final_output
            + "\n\n---\nSave this somewhere handy. Good luck — you've got this! 💪"
        )
    )

    return {
        "final_output": final_output,
        "finished": True,
        "messages": [delivery_message],
    }


async def _save_final_output(state: XBuddyState, final_output: str) -> None:
    """Save the training program to Supabase. Skips silently if not configured."""
    try:
        from integrations.supabase.supabase_client import SupabaseClient
        supabase = SupabaseClient()

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: supabase.save_business_plan(
                user_id=state.get("user_id", 1),
                thread_id=state.get("thread_id", ""),
                content=final_output,
                markdown_content=final_output,
                agent_id="xbuddy",
            ),
        )
        logger.info("[implementation] Training program saved to Supabase")

    except (ImportError, ValueError):
        logger.debug("[implementation] Supabase not configured, skipping save")
    except Exception as e:
        logger.warning(f"[implementation] Supabase save failed: {e}")
