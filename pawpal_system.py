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
        pass

    def filter_tasks(self, by_status: bool = None, pet_name: str = None) -> List[Task]:
        """Return tasks filtered by completion status and/or pet name."""
        pass

    def mark_task_complete(self, task: Task) -> None:
        """Mark the given task complete and handle recurrence if needed."""
        pass

    def detect_conflicts(self) -> List[str]:
        """Return warning messages for tasks scheduled at the same time."""
        pass