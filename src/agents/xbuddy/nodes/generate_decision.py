"""Generate decision node — makes a structured decision about what happens next.

This is a second, separate LLM call that uses structured output (Pydantic schema)
to decide: should we stay on this section, move to the next, or go back to a previous one?

Keeping this separate from generate_reply means the conversational response
and the navigation logic never get confused — one node talks, one node decides.
"""

import logging
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig

from core.llm import get_model
from ..models import ChatAgentDecision, ChatAgentOutput, XBuddyState

logger = logging.getLogger(__name__)

# Prompt that instructs the LLM to analyze the conversation and return a structured decision
DECISION_SYSTEM_PROMPT = """You are a decision engine for a fitness coaching conversation.

Analyze the last exchange and return a structured decision.

ROUTER DIRECTIVE RULES:
- Return "next" ONLY if: the user explicitly confirmed they are satisfied (said "yes", "looks good",
  "that's correct", or equivalent), AND the current section summary has been presented.
- Return "stay" if: the user is still answering questions, hasn't confirmed yet, wants changes,
  or the section summary hasn't been presented yet.
- Return "modify:<section_id>" if: the user wants to go back to a specific previous section.
  Valid section IDs: goals, fitness, schedule, nutrition, lifestyle.

SHOULD_SAVE_CONTENT RULES:
- Set to true ONLY when the user confirmed satisfaction (i.e., you're returning "next").
- Otherwise false.

IS_SATISFIED RULES:
- true if the user explicitly confirmed the summary is correct
- false or null otherwise
"""


async def generate_decision_node(state: XBuddyState, config: RunnableConfig) -> dict:
    """Analyze the conversation and return a structured navigation decision.

    Uses .with_structured_output() so the LLM returns a validated ChatAgentDecision
    object instead of raw text — no parsing needed.
    """
    messages = state.get("messages", [])
    current_section = state.get("current_section")

    # Get the last human and AI messages for context
    last_human = next(
        (m.content for m in reversed(messages) if isinstance(m, HumanMessage)), ""
    )
    last_ai = next(
        (m.content for m in reversed(messages) if isinstance(m, AIMessage)), ""
    )

    decision_prompt = f"""Current section: {current_section.value}

Last user message: {last_human}

Last AI response: {last_ai}

Based on this exchange, make your decision."""

    logger.info(f"[generate_decision] section={current_section.value}")

    # with_structured_output tells LangChain to return a ChatAgentDecision object
    model = get_model().with_structured_output(ChatAgentDecision)
    decision: ChatAgentDecision = await model.ainvoke(
        [
            HumanMessage(content=DECISION_SYSTEM_PROMPT + "\n\n" + decision_prompt)
        ],
        config=config,
    )

    logger.info(
        f"[generate_decision] directive={decision.router_directive} "
        f"satisfied={decision.is_satisfied} save={decision.should_save_content}"
    )

    # Package the decision alongside the last AI reply into agent_output
    agent_output = ChatAgentOutput(
        reply=last_ai,
        router_directive=decision.router_directive,
        user_satisfaction_feedback=decision.user_satisfaction_feedback,
        is_satisfied=decision.is_satisfied,
        should_save_content=decision.should_save_content,
    )

    return {
        "router_directive": decision.router_directive,
        "agent_output": agent_output,
        "awaiting_user_input": True,
    }
