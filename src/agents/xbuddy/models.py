"""Pydantic models for your XBuddy Agent.

Study FounderBuddy's models.py to understand how these work:
https://github.com/Victoria824/FounderBuddy/blob/main/src/agents/founder_buddy/models.py
"""

import uuid
from typing import Any

from langchain_core.messages import BaseMessage
from langgraph.graph import MessagesState
from pydantic import BaseModel, Field, field_validator

from .enums import RouterDirective, SectionID, SectionStatus
from .sections.base_prompt import SectionTemplate, ValidationRule


class SectionContent(BaseModel):
    """Content for an agent section."""
    content: dict[str, Any]  # Rich text content (Tiptap JSON format)
    plain_text: str | None = None  # Plain text version for LLM processing


class SectionState(BaseModel):
    """State of a single section."""
    section_id: SectionID
    content: SectionContent | None = None
    satisfaction_status: str | None = None  # satisfied, needs_improvement, or None
    status: SectionStatus = SectionStatus.PENDING


class ContextPacket(BaseModel):
    """Context packet loaded by the router for the current section."""
    section_id: SectionID
    status: SectionStatus
    system_prompt: str
    draft: SectionContent | None = None
    validation_rules: dict[str, Any] | None = None


class XBuddyData(BaseModel):
    """Structured fitness data collected across the 5 conversation sections.

    These fields are progressively filled in as the user moves through sections.
    The implementation node uses all of them to generate the final training program.
    """
    # Section 1: Goals
    primary_goal: str | None = None          # e.g. "lose weight", "build muscle", "run 5k"
    goal_timeline_weeks: int | None = None   # e.g. 12
    motivation: str | None = None            # why they want this

    # Section 2: Current Fitness
    fitness_level: str | None = None         # beginner / intermediate / advanced
    injuries_or_limitations: list[str] = []  # e.g. ["bad knees", "lower back pain"]
    exercise_history: str | None = None      # what they've tried before

    # Section 3: Schedule & Equipment
    days_per_week: int | None = None         # how many days available to train
    session_duration_minutes: int | None = None
    equipment: list[str] = []               # e.g. ["gym", "dumbbells", "resistance bands"]
    preferred_workout_style: str | None = None  # e.g. "lifting", "cardio", "mixed"

    # Section 4: Nutrition
    dietary_restrictions: list[str] = []    # e.g. ["vegetarian", "gluten-free"]
    meal_frequency: int | None = None       # meals per day
    nutrition_goal: str | None = None       # e.g. "calorie deficit", "high protein"

    # Section 5: Lifestyle
    sleep_hours: float | None = None        # average hours per night
    stress_level: str | None = None         # low / medium / high
    daily_activity: str | None = None       # sedentary / lightly active / very active


class ChatAgentDecision(BaseModel):
    """Structured decision from the generate_decision node."""
    router_directive: str = Field(
        ...,
        description="Navigation control: 'stay', 'next', or 'modify:<section_id>'",
    )
    user_satisfaction_feedback: str | None = Field(
        None, description="User's feedback about satisfaction with the section."
    )
    is_satisfied: bool | None = Field(
        None, description="Whether the user is satisfied with the current section."
    )
    should_save_content: bool = Field(
        False,
        description="Whether to save the current section content.",
    )

    @field_validator("router_directive")
    def validate_router_directive(cls, v):
        if v not in ["stay", "next"] and not v.startswith("modify:"):
            raise ValueError("router_directive must be 'stay', 'next', or 'modify:<section_id>'")
        return v


class ChatAgentOutput(BaseModel):
    """Complete output from the generate_reply + generate_decision nodes."""
    reply: str = Field(..., description="Conversational response to the user.")
    router_directive: str = Field(
        ...,
        description="Navigation control: 'stay', 'next', or 'modify:<section_id>'",
    )
    user_satisfaction_feedback: str | None = None
    is_satisfied: bool | None = None
    should_save_content: bool = False

    @field_validator("router_directive")
    def validate_router_directive(cls, v):
        if v not in ["stay", "next"] and not v.startswith("modify:"):
            raise ValueError("router_directive must be 'stay', 'next', or 'modify:<section_id>'")
        return v


class XBuddyState(MessagesState):
    """State for your XBuddy agent.

    Extends MessagesState (which provides `messages: list[BaseMessage]`).
    Study FounderBuddyState to understand each field's role in the graph.
    """
    # User and conversation identification
    user_id: int = 1
    thread_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    # Navigation and progress
    current_section: SectionID = SectionID.GOALS
    context_packet: ContextPacket | None = None
    section_states: dict[str, SectionState] = Field(default_factory=dict)
    router_directive: str = RouterDirective.NEXT
    finished: bool = False

    # Domain-specific data — TODO: customize XBuddyData above
    user_data: XBuddyData = Field(default_factory=XBuddyData)

    # Memory management
    short_memory: list[BaseMessage] = Field(default_factory=list)

    # Agent output
    agent_output: ChatAgentOutput | None = None
    awaiting_user_input: bool = False
    awaiting_satisfaction_feedback: bool = False

    # Error tracking
    error_count: int = 0
    last_error: str | None = None

    # Final output — TODO: rename to match your domain
    final_output: str | None = None
    should_generate_final_output: bool = False
