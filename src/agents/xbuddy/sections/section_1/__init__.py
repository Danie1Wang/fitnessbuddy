"""Section 1: Goals — What does the user want to achieve?

Gathers the user's primary fitness goal, their timeline, and their motivation.
Motivation is important because it shapes how the program is framed and communicated.
"""

from ...enums import SectionID
from ..base_prompt import BASE_RULES, SectionTemplate

SECTION_1_TEMPLATE = SectionTemplate(
    section_id=SectionID.GOALS,
    name="Fitness Goals",
    description="Understand what the user wants to achieve, by when, and why",
    system_prompt_template=BASE_RULES + """
## Current Section: Fitness Goals

Your job in this section is to understand three things:
1. **Primary goal** — what specific outcome they want (e.g. lose 10kg, run a 5k, build muscle)
2. **Timeline** — how many weeks they want to achieve it in
3. **Motivation** — the real reason behind the goal (e.g. "wedding in 3 months", "feel confident again")

Start by asking what they want to achieve. Then naturally ask about timeline and motivation.

Example opening: "Hey! I'm FitnessBuddy — I'm going to help you build a training program
tailored just for you. Let's start with the most important question: what's your main fitness goal?"

Once you have all three, present your summary and ask for confirmation before moving on.
""",
    required_fields=["primary_goal", "goal_timeline_weeks", "motivation"],
    next_section=SectionID.FITNESS,
)
