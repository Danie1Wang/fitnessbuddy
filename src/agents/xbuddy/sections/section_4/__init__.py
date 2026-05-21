"""Section 4: Nutrition — What does the user eat?

Gathers dietary preferences, restrictions, and nutrition goals.
Training without nutrition awareness gets half the results.
"""

from ...enums import SectionID
from ..base_prompt import BASE_RULES, SectionTemplate

SECTION_4_TEMPLATE = SectionTemplate(
    section_id=SectionID.NUTRITION,
    name="Nutrition Habits",
    description="Understand dietary preferences, restrictions, and eating patterns",
    system_prompt_template=BASE_RULES + """
## Current Section: Nutrition Habits

Your job is to understand the user's relationship with food:
1. **Dietary restrictions** — vegetarian, vegan, gluten-free, halal, allergies, etc.
2. **Meal frequency** — how many times a day they typically eat
3. **Nutrition goal** — are they trying to lose fat (calorie deficit), gain muscle (calorie surplus), or maintain?

Keep this section light and non-judgmental. Don't make them feel like their eating habits are wrong.
Focus on what works for them, not what's theoretically optimal.

If they say they don't know much about nutrition, briefly explain the key concept relevant to their
fitness goal (e.g. "for weight loss, eating slightly less than you burn is the main lever").

Ask about dietary restrictions first, then meal frequency, then nutrition goal.
""",
    required_fields=["nutrition_goal"],
    next_section=SectionID.LIFESTYLE,
)
