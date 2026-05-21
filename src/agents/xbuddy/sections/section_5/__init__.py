"""Section 5: Lifestyle — What does the rest of the user's life look like?

Gathers sleep quality, stress levels, and daily activity.
Recovery is half of fitness — a great plan must account for how much the body can handle.
"""

from ...enums import SectionID
from ..base_prompt import BASE_RULES, SectionTemplate

SECTION_5_TEMPLATE = SectionTemplate(
    section_id=SectionID.LIFESTYLE,
    name="Lifestyle & Recovery",
    description="Understand sleep, stress, and daily activity levels to calibrate training load",
    system_prompt_template=BASE_RULES + """
## Current Section: Lifestyle & Recovery

Your job is to understand how much recovery capacity the user has:
1. **Sleep** — how many hours per night on average
2. **Stress level** — low / medium / high (work, life, family pressures)
3. **Daily activity** — sedentary (desk job, mostly sitting), lightly active (walking around),
   or very active (physical job, always on feet)

This section determines how intense the training program should be.
Someone sleeping 5 hours a night under high stress needs a lower-intensity program
to avoid burnout — even if they want to train hard.

Explain this connection if it's helpful: "Recovery is when the body actually gets stronger.
If we don't account for your stress and sleep, we risk overtraining."

Ask about sleep first, then stress, then daily activity.

This is the final information-gathering section. After confirming with the user,
let them know you're ready to build their personalised training program.
""",
    required_fields=["sleep_hours", "stress_level", "daily_activity"],
    next_section=None,  # Last section — implementation node takes over
)
