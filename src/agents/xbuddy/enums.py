"""Enumerations for your XBuddy Agent."""

from enum import Enum


class SectionStatus(str, Enum):
    """Status of an agent section."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class RouterDirective(str, Enum):
    """Router directive for navigation control."""
    STAY = "stay"
    NEXT = "next"
    MODIFY = "modify"  # Format: "modify:section_id"


class SectionID(str, Enum):
    """FitnessBuddy conversation sections.

    Each section collects a specific type of information from the user:
      GOALS       - What they want to achieve and why
      FITNESS     - Current fitness level, injuries, experience
      SCHEDULE    - Availability, equipment, preferred workout style
      NUTRITION   - Diet preferences, restrictions, eating habits
      LIFESTYLE   - Sleep, stress, daily activity outside workouts
    """
    GOALS = "goals"
    FITNESS = "fitness"
    SCHEDULE = "schedule"
    NUTRITION = "nutrition"
    LIFESTYLE = "lifestyle"
