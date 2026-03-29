"""
pawpal_system.py — Core class skeletons for PawPal+.

Classes:
    Task      : A single pet care activity.
    Pet       : A pet and its list of tasks.
    Owner     : An owner who manages multiple pets.
    Scheduler : Retrieves, organizes, and manages tasks across pets.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """A single pet care activity."""

    description: str
    time: str           # HH:MM format
    frequency: str      # "daily", "weekly", or "once"
    is_complete: bool = False

    def mark_complete(self) -> None:
        """Mark this task as complete."""
        self.is_complete = True


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    """A pet and its associated tasks."""

    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def get_tasks(self) -> List[Task]:
        """Return all tasks for this pet."""
        return self.tasks


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

@dataclass
class Owner:
    """An owner who manages multiple pets."""

    name: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list."""
        self.pets.append(pet)

    def get_all_tasks(self) -> List[Task]:
        """Return all tasks across all pets."""
        return [task for pet in self.pets for task in pet.tasks]


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    """Retrieves, organizes, and manages tasks across all of an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        self.owner: Owner = owner

    def get_schedule(self) -> List[Task]:
        """Return all tasks across all pets."""
        return self.owner.get_all_tasks()

    def sort_by_time(self) -> List[Task]:
        """Return all tasks sorted by time in HH:MM order."""
        return sorted(self.get_schedule(), key=lambda t: t.time)

    def filter_tasks(self, by_status: bool = None, pet_name: str = None) -> List[Task]:
        """Return tasks filtered by completion status and/or pet name.

        Args:
            by_status: If True, return only completed tasks.
                       If False, return only pending tasks.
                       If None, do not filter by status.
            pet_name:  If provided, return only tasks belonging to that pet.
                       If None, include tasks from all pets.
        """
        results = []
        for pet in self.owner.pets:
            if pet_name is not None and pet.name.lower() != pet_name.lower():
                continue
            for task in pet.tasks:
                if by_status is not None and task.is_complete != by_status:
                    continue
                results.append(task)
        return results

    def mark_task_complete(self, task: Task) -> None:
        """Mark the given task complete and schedule the next occurrence.

        For daily tasks, a new task is added for tomorrow.
        For weekly tasks, a new task is added for seven days from today.
        For once tasks, the task is simply marked complete with no recurrence.
        """
        task.mark_complete()

        if task.frequency == "once":
            return

        # Calculate the next due date and encode it in the description.
        today = date.today()
        if task.frequency == "daily":
            next_date = today + timedelta(days=1)
        else:  # weekly
            next_date = today + timedelta(weeks=1)

        next_task = Task(
            description=task.description,
            time=task.time,
            frequency=task.frequency,
        )

        # Add the new task to the correct pet's list.
        for pet in self.owner.pets:
            if task in pet.tasks:
                pet.add_task(next_task)
                break

    def detect_conflicts(self) -> List[str]:
        """Return warning messages for tasks scheduled at the same time.

        Two tasks conflict when they share the same HH:MM time slot,
        regardless of whether they belong to the same pet.
        """
        seen: dict = {}          # time -> first task description
        warnings: List[str] = []

        for pet in self.owner.pets:
            for task in pet.tasks:
                if task.time in seen:
                    warnings.append(
                        f"Conflict at {task.time}: "
                        f'"{seen[task.time]}" and "{task.description}" '
                        f"(pet: {pet.name})"
                    )
                else:
                    seen[task.time] = task.description

        return warnings