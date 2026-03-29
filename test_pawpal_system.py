"""
test_pawpal_system.py — pytest tests for pawpal_system.py.

Covers: sort_by_time, filter_tasks, mark_task_complete, detect_conflicts.
"""

import pytest
from pawpal_system import Owner, Pet, Task, Scheduler


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_scheduler(*pets: Pet) -> Scheduler:
    owner = Owner(name="Jordan")
    for pet in pets:
        owner.add_pet(pet)
    return Scheduler(owner=owner)


def make_pet(name: str, species: str = "dog", tasks=()) -> Pet:
    pet = Pet(name=name, species=species)
    for task in tasks:
        pet.add_task(task)
    return pet


# ---------------------------------------------------------------------------
# sort_by_time
# ---------------------------------------------------------------------------

class TestSortByTime:
    def test_returns_tasks_in_chronological_order(self):
        """Tasks added out of order should come back sorted by HH:MM."""
        pet = make_pet("Mochi", tasks=[
            Task(description="Evening walk", time="18:00", frequency="daily"),
            Task(description="Morning feed",  time="07:00", frequency="daily"),
            Task(description="Medication",    time="08:30", frequency="daily"),
        ])
        scheduler = make_scheduler(pet)
        sorted_tasks = scheduler.sort_by_time()
        times = [t.time for t in sorted_tasks]
        assert times == ["07:00", "08:30", "18:00"]

    def test_single_task_returns_unchanged(self):
        """A single task should be returned as-is."""
        pet = make_pet("Buddy", tasks=[Task(description="Walk", time="09:00", frequency="daily")])
        scheduler = make_scheduler(pet)
        assert len(scheduler.sort_by_time()) == 1

    def test_tasks_across_multiple_pets_are_sorted_together(self):
        """Tasks from different pets should be merged and sorted by time."""
        cat = make_pet("Mochi", tasks=[Task(description="Feed cat",  time="08:00", frequency="daily")])
        dog = make_pet("Buddy", tasks=[Task(description="Walk dog",  time="07:00", frequency="daily")])
        scheduler = make_scheduler(cat, dog)
        times = [t.time for t in scheduler.sort_by_time()]
        assert times == sorted(times)


# ---------------------------------------------------------------------------
# filter_tasks
# ---------------------------------------------------------------------------

class TestFilterTasks:
    def setup_method(self):
        walk = Task(description="Walk",      time="07:00", frequency="daily")
        feed = Task(description="Feed",      time="08:00", frequency="daily")
        meds = Task(description="Meds",      time="09:00", frequency="daily")
        feed.mark_complete()

        self.mochi = make_pet("Mochi", tasks=[walk, feed])
        self.buddy = make_pet("Buddy", tasks=[meds])
        self.scheduler = make_scheduler(self.mochi, self.buddy)

    def test_filter_by_status_pending(self):
        """by_status=False returns only incomplete tasks."""
        pending = self.scheduler.filter_tasks(by_status=False)
        assert all(not t.is_complete for t in pending)
        assert len(pending) == 2  # Walk (Mochi) + Meds (Buddy)

    def test_filter_by_status_complete(self):
        """by_status=True returns only completed tasks."""
        done = self.scheduler.filter_tasks(by_status=True)
        assert all(t.is_complete for t in done)
        assert len(done) == 1
        assert done[0].description == "Feed"

    def test_filter_by_pet_name(self):
        """pet_name filter returns only tasks belonging to that pet."""
        mochi_tasks = self.scheduler.filter_tasks(pet_name="Mochi")
        assert len(mochi_tasks) == 2
        assert all(t in self.mochi.tasks for t in mochi_tasks)

    def test_filter_by_pet_name_case_insensitive(self):
        """Pet name matching should be case-insensitive."""
        assert self.scheduler.filter_tasks(pet_name="mochi") == \
               self.scheduler.filter_tasks(pet_name="Mochi")

    def test_filter_by_status_and_pet_name_combined(self):
        """Combining both filters should apply both constraints."""
        result = self.scheduler.filter_tasks(by_status=False, pet_name="Mochi")
        assert len(result) == 1
        assert result[0].description == "Walk"

    def test_no_filters_returns_all_tasks(self):
        """Calling filter_tasks with no arguments returns every task."""
        all_tasks = self.scheduler.filter_tasks()
        assert len(all_tasks) == 3


# ---------------------------------------------------------------------------
# mark_task_complete
# ---------------------------------------------------------------------------

class TestMarkTaskComplete:
    def test_once_task_is_marked_complete(self):
        """A once task should be marked complete with no new task created."""
        task = Task(description="Vet visit", time="10:00", frequency="once")
        pet = make_pet("Mochi", tasks=[task])
        scheduler = make_scheduler(pet)

        scheduler.mark_task_complete(task)

        assert task.is_complete is True
        assert len(pet.tasks) == 1  # no new task

    def test_daily_task_creates_new_pending_task(self):
        """Completing a daily task should append a new pending task to the pet."""
        task = Task(description="Walk", time="07:00", frequency="daily")
        pet = make_pet("Buddy", tasks=[task])
        scheduler = make_scheduler(pet)

        scheduler.mark_task_complete(task)

        assert task.is_complete is True
        assert len(pet.tasks) == 2
        new_task = pet.tasks[1]
        assert new_task.is_complete is False
        assert new_task.description == task.description
        assert new_task.frequency == "daily"

    def test_weekly_task_creates_new_pending_task(self):
        """Completing a weekly task should append a new pending task to the pet."""
        task = Task(description="Grooming", time="10:00", frequency="weekly")
        pet = make_pet("Mochi", tasks=[task])
        scheduler = make_scheduler(pet)

        scheduler.mark_task_complete(task)

        assert task.is_complete is True
        assert len(pet.tasks) == 2
        assert pet.tasks[1].frequency == "weekly"

    def test_new_recurring_task_preserves_time(self):
        """The new task for a recurring task should keep the same time slot."""
        task = Task(description="Feed", time="08:00", frequency="daily")
        pet = make_pet("Mochi", tasks=[task])
        scheduler = make_scheduler(pet)

        scheduler.mark_task_complete(task)

        assert pet.tasks[1].time == "08:00"


# ---------------------------------------------------------------------------
# detect_conflicts
# ---------------------------------------------------------------------------

class TestDetectConflicts:
    def test_no_conflicts_when_times_are_unique(self):
        """No warnings when all tasks have different time slots."""
        pet = make_pet("Mochi", tasks=[
            Task(description="Feed",  time="07:00", frequency="daily"),
            Task(description="Walk",  time="08:00", frequency="daily"),
            Task(description="Meds",  time="09:00", frequency="daily"),
        ])
        scheduler = make_scheduler(pet)
        assert scheduler.detect_conflicts() == []

    def test_conflict_detected_for_same_time(self):
        """Two tasks at the same time should produce a warning."""
        pet = make_pet("Buddy", tasks=[
            Task(description="Walk",  time="07:00", frequency="daily"),
            Task(description="Feed",  time="07:00", frequency="daily"),
        ])
        scheduler = make_scheduler(pet)
        conflicts = scheduler.detect_conflicts()
        assert len(conflicts) == 1
        assert "07:00" in conflicts[0]

    def test_conflict_detected_across_pets(self):
        """Tasks at the same time across different pets should also conflict."""
        cat = make_pet("Mochi", tasks=[Task(description="Feed cat", time="08:00", frequency="daily")])
        dog = make_pet("Buddy", tasks=[Task(description="Feed dog", time="08:00", frequency="daily")])
        scheduler = make_scheduler(cat, dog)
        conflicts = scheduler.detect_conflicts()
        assert len(conflicts) == 1
        assert "08:00" in conflicts[0]

    def test_multiple_conflicts_all_reported(self):
        """Every conflicting time slot should produce its own warning."""
        pet = make_pet("Mochi", tasks=[
            Task(description="A", time="07:00", frequency="daily"),
            Task(description="B", time="07:00", frequency="daily"),
            Task(description="C", time="09:00", frequency="daily"),
            Task(description="D", time="09:00", frequency="daily"),
        ])
        scheduler = make_scheduler(pet)
        assert len(scheduler.detect_conflicts()) == 2