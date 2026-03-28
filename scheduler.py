"""
scheduler.py — Core scheduling logic for PawPal+.

Provides:
  - Task        : a single pet-care task with title, duration, and priority.
  - ScheduleResult : the output of a scheduling run (selected tasks + explanation).
  - Scheduler   : selects and orders tasks to fit within a time budget.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List


# ---------------------------------------------------------------------------
# Priority
# ---------------------------------------------------------------------------

class Priority(str, Enum):
    """Ordered priority levels. Higher ordinal == higher urgency."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

    def rank(self) -> int:
        """Return a numeric rank so tasks can be sorted (higher is more urgent)."""
        return {"low": 0, "medium": 1, "high": 2}[self.value]


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """A single pet-care task.

    Attributes:
        title:    Short human-readable name (e.g. "Morning walk").
        duration: How long the task takes, in minutes. Must be >= 1.
        priority: Urgency level — low, medium, or high.
    """

    title: str
    duration: int          # minutes
    priority: Priority

    def __post_init__(self) -> None:
        if self.duration < 1:
            raise ValueError(f"duration must be >= 1, got {self.duration}")
        # Accept plain strings ("high") as well as Priority enum values.
        if not isinstance(self.priority, Priority):
            self.priority = Priority(self.priority)


# ---------------------------------------------------------------------------
# ScheduleResult
# ---------------------------------------------------------------------------

@dataclass
class ScheduleResult:
    """The output of a scheduling run.

    Attributes:
        selected:    Tasks chosen for today, in the order they should be done.
        skipped:     Tasks that were left out (not enough time or lower priority).
        explanation: A human-readable summary of the scheduling decisions.
        total_time:  Total minutes consumed by the selected tasks.
    """

    selected: List[Task]
    skipped: List[Task]
    explanation: str
    total_time: int = field(init=False)

    def __post_init__(self) -> None:
        self.total_time = sum(t.duration for t in self.selected)


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    """Selects and orders pet-care tasks to fit within a time budget.

    Strategy
    --------
    1. Sort all tasks by priority (high → low). Ties are broken by shorter
       duration first, so you squeeze in more tasks when time is tight.
    2. Greedily pick tasks in that order until the budget is exhausted.
    3. Return the chosen tasks sorted the same way (highest priority first),
       which is also a reasonable execution order for the day.

    Usage
    -----
    >>> scheduler = Scheduler(time_budget_minutes=60)
    >>> result = scheduler.schedule(tasks)
    >>> print(result.explanation)
    """

    def __init__(self, time_budget_minutes: int) -> None:
        """
        Args:
            time_budget_minutes: Total minutes available for pet care today.
                                 Must be >= 1.
        """
        if time_budget_minutes < 1:
            raise ValueError(
                f"time_budget_minutes must be >= 1, got {time_budget_minutes}"
            )
        self.time_budget_minutes = time_budget_minutes

    def schedule(self, tasks: List[Task]) -> ScheduleResult:
        """Build a daily schedule from the given task list.

        Args:
            tasks: All candidate tasks. May be empty.

        Returns:
            A ScheduleResult with the chosen tasks, skipped tasks, and an
            explanation of every decision made.
        """
        if not tasks:
            return ScheduleResult(
                selected=[],
                skipped=[],
                explanation="No tasks were provided, so the schedule is empty.",
            )

        # Sort: primary key = priority (desc), secondary = duration (asc).
        ranked = sorted(tasks, key=lambda t: (-t.priority.rank(), t.duration))

        selected: List[Task] = []
        skipped: List[Task] = []
        remaining = self.time_budget_minutes

        for task in ranked:
            if task.duration <= remaining:
                selected.append(task)
                remaining -= task.duration
            else:
                skipped.append(task)

        explanation = self._build_explanation(
            selected=selected,
            skipped=skipped,
            budget=self.time_budget_minutes,
            remaining=remaining,
        )

        return ScheduleResult(selected=selected, skipped=skipped, explanation=explanation)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_explanation(
        selected: List[Task],
        skipped: List[Task],
        budget: int,
        remaining: int,
    ) -> str:
        """Compose a plain-English explanation of the scheduling decisions."""
        lines: List[str] = []

        lines.append(f"Time budget: {budget} min.")

        if selected:
            lines.append(
                f"\n{len(selected)} task(s) scheduled "
                f"({budget - remaining} min used, {remaining} min free):"
            )
            for task in selected:
                lines.append(
                    f"  • {task.title} — {task.duration} min [{task.priority.value} priority]"
                )
        else:
            lines.append("\nNo tasks could fit within the time budget.")

        if skipped:
            lines.append(f"\n{len(skipped)} task(s) skipped (insufficient time remaining):")
            for task in skipped:
                lines.append(
                    f"  • {task.title} — {task.duration} min [{task.priority.value} priority]"
                )

        return "\n".join(lines)
