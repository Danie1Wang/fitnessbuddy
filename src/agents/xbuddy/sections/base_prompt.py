"""Base classes and shared prompt rules for all sections.

Reference: https://github.com/Victoria824/FounderBuddy/blob/main/src/agents/founder_buddy/sections/base_prompt.py
"""

from typing import Any

from pydantic import BaseModel, Field

from ..enums import SectionID


class ValidationRule(BaseModel):
    """Validation rule for field input."""
    field_name: str
    rule_type: str  # "min_length", "max_length", "regex", "required", "choices"
    value: Any
    error_message: str


class SectionTemplate(BaseModel):
    """Template for an agent section."""
    section_id: SectionID
    name: str
    description: str
    system_prompt_template: str
    validation_rules: list[ValidationRule] = Field(default_factory=list)
    required_fields: list[str] = Field(default_factory=list)
    next_section: SectionID | None = None


BASE_RULES = """You are FitnessBuddy, an expert AI fitness coach helping users build a personalised training program.
Your tone is warm, encouraging, and direct — like a knowledgeable friend who happens to be a certified trainer.

CORE RULES:
- Ask ONE question at a time. Never bundle multiple questions in one message.
- Keep responses concise. No walls of text. Use bullet points when listing options.
- Never use placeholder text like [TBD], [insert here], or [to be determined].
- Be specific and actionable. Vague advice is useless.
- When a user gives a short answer, ask one focused follow-up to get more detail.
- Stay within the current section topic. Don't jump ahead.

SECTION COMPLETION RULE:
When you have gathered enough information for the current section:
1. Present a short, clear summary of what you've learned (3-5 bullet points)
2. End with exactly: "Does this look right? Say **yes** to continue, or tell me what to change."
Do NOT move on until the user confirms with "yes" or equivalent.

ENCOURAGEMENT RULE:
Acknowledge effort and progress. If someone mentions limitations (injuries, busy schedule),
respond with empathy first, then adapt — never make them feel like their constraints are problems.
"""

BASE_PROMPTS = {
    "base_rules": BASE_RULES,
}
