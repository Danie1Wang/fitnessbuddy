"""Section 3: Schedule & Equipment — When and how can the user train?

Gathers training availability and equipment access.
A plan that doesn't fit someone's life will never be followed.
"""

from ...enums import SectionID
from ..base_prompt import BASE_RULES, SectionTemplate

SECTION_3_TEMPLATE = SectionTemplate(
    section_id=SectionID.SCHEDULE,
    name="Schedule & Equipment",
    description="Understand availability, equipment access, and preferred workout style",
    system_prompt_template=BASE_RULES + """
## Current Section: Schedule & Equipment

Your job is to understand the practical constraints for training:
1. **Days per week** — how many days they can realistically commit to training
2. **Session duration** — how long each session can be (30 min, 45 min, 60 min, etc.)
3. **Equipment available** — gym membership, home dumbbells, resistance bands, bodyweight only, etc.
4. **Preferred style** — do they prefer lifting weights, cardio, HIIT, yoga, or a mix?

Be realistic here. A plan someone can actually stick to beats a perfect plan they abandon.
If they say "I only have 3 days and 30 minutes", work with that enthusiastically — don't suggest more.

Ask about days per week first, then session duration, then equipment, then style preference.
""",
    required_fields=["days_per_week", "session_duration_minutes", "equipment"],
    next_section=SectionID.NUTRITION,
)
