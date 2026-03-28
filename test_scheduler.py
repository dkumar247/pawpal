"""
test_scheduler.py — pytest tests for the PawPal+ scheduling logic.
"""

import pytest
from scheduler import Priority, Task, Scheduler


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_task(title: str, duration: int, priority: str) -> Task:
    return Task(title=title, duration=duration, priority=priority)


# ---------------------------------------------------------------------------
# Priority selection
# ---------------------------------------------------------------------------

def test_high_priority_selected_over_low_when_budget_is_tight():
    """When only one task fits, the highest-priority task wins."""
    tasks = [
        make_task("Low-priority task",  duration=30, priority="low"),
        make_task("High-priority task", duration=30, priority="high"),
    ]
    result = Scheduler(time_budget_minutes=30).schedule(tasks)

    titles = [t.title for t in result.selected]
    assert "High-priority task" in titles
    assert "Low-priority task" not in titles


def test_medium_priority_selected_over_low():
    """Medium-priority tasks are preferred over low-priority ones."""
    tasks = [
        make_task("Low task",    duration=20, priority="low"),
        make_task("Medium task", duration=20, priority="medium"),
    ]
    result = Scheduler(time_budget_minutes=20).schedule(tasks)

    assert result.selected[0].title == "Medium task"
    assert any(t.title == "Low task" for t in result.skipped)


def test_all_priorities_ordered_correctly():
    """All three tasks fit; they are returned high → medium → low."""
    tasks = [
        make_task("Low",    duration=10, priority="low"),
        make_task("High",   duration=10, priority="high"),
        make_task("Medium", duration=10, priority="medium"),
    ]
    result = Scheduler(time_budget_minutes=60).schedule(tasks)

    assert len(result.selected) == 3
    assert [t.title for t in result.selected] == ["High", "Medium", "Low"]


# ---------------------------------------------------------------------------
# Tasks that do not fit are skipped
# ---------------------------------------------------------------------------

def test_task_too_long_for_remaining_time_is_skipped():
    """A task that exceeds the remaining budget is moved to skipped."""
    tasks = [
        make_task("Quick task", duration=10, priority="high"),
        make_task("Long task",  duration=60, priority="high"),
    ]
    result = Scheduler(time_budget_minutes=15).schedule(tasks)

    assert any(t.title == "Quick task" for t in result.selected)
    assert any(t.title == "Long task"  for t in result.skipped)


def test_no_tasks_fit_within_budget():
    """When every task exceeds the budget, selected is empty."""
    tasks = [
        make_task("Long A", duration=90, priority="high"),
        make_task("Long B", duration=120, priority="medium"),
    ]
    result = Scheduler(time_budget_minutes=30).schedule(tasks)

    assert result.selected == []
    assert len(result.skipped) == 2


# ---------------------------------------------------------------------------
# Total scheduled time never exceeds budget
# ---------------------------------------------------------------------------

def test_total_time_within_budget_simple():
    """total_time must not exceed the declared budget."""
    tasks = [make_task(f"Task {i}", duration=15, priority="medium") for i in range(6)]
    budget = 60
    result = Scheduler(time_budget_minutes=budget).schedule(tasks)

    assert result.total_time <= budget


def test_total_time_within_budget_mixed_priorities():
    """Budget constraint holds even with a mix of priorities and durations."""
    tasks = [
        make_task("A", duration=25, priority="high"),
        make_task("B", duration=25, priority="high"),
        make_task("C", duration=25, priority="medium"),
        make_task("D", duration=25, priority="low"),
    ]
    budget = 60
    result = Scheduler(time_budget_minutes=budget).schedule(tasks)

    assert result.total_time <= budget


def test_total_time_matches_sum_of_selected_durations():
    """ScheduleResult.total_time equals sum of selected task durations."""
    tasks = [
        make_task("Walk",  duration=20, priority="high"),
        make_task("Feed",  duration=10, priority="high"),
        make_task("Groom", duration=15, priority="medium"),
    ]
    result = Scheduler(time_budget_minutes=60).schedule(tasks)

    assert result.total_time == sum(t.duration for t in result.selected)


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------

def test_same_input_produces_same_output():
    """Calling schedule twice with identical inputs returns identical results."""
    tasks = [
        make_task("Walk",    duration=20, priority="high"),
        make_task("Feed",    duration=10, priority="high"),
        make_task("Play",    duration=30, priority="medium"),
        make_task("Groom",   duration=45, priority="low"),
    ]
    s = Scheduler(time_budget_minutes=60)

    result_a = s.schedule(tasks)
    result_b = s.schedule(tasks)

    assert [t.title for t in result_a.selected] == [t.title for t in result_b.selected]
    assert [t.title for t in result_a.skipped]  == [t.title for t in result_b.skipped]
    assert result_a.explanation == result_b.explanation


def test_input_list_order_does_not_affect_outcome():
    """Shuffling the input list should not change which tasks are selected."""
    tasks_forward = [
        make_task("Low task",  duration=20, priority="low"),
        make_task("High task", duration=20, priority="high"),
    ]
    tasks_reversed = list(reversed(tasks_forward))

    result_a = Scheduler(time_budget_minutes=20).schedule(tasks_forward)
    result_b = Scheduler(time_budget_minutes=20).schedule(tasks_reversed)

    assert {t.title for t in result_a.selected} == {t.title for t in result_b.selected}
    assert {t.title for t in result_a.skipped}  == {t.title for t in result_b.skipped}


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_empty_task_list():
    """An empty task list returns empty selected and skipped lists."""
    result = Scheduler(time_budget_minutes=60).schedule([])

    assert result.selected == []
    assert result.skipped  == []


def test_single_task_fits_exactly():
    """A single task that exactly fills the budget is selected."""
    tasks = [make_task("Exact fit", duration=60, priority="medium")]
    result = Scheduler(time_budget_minutes=60).schedule(tasks)

    assert len(result.selected) == 1
    assert result.skipped == []
    assert result.total_time == 60


def test_explanation_mentions_scheduled_and_skipped_tasks():
    """The explanation references both selected and skipped task titles."""
    tasks = [
        make_task("Morning walk", duration=20, priority="high"),
        make_task("Bath time",    duration=60, priority="low"),
    ]
    result = Scheduler(time_budget_minutes=20).schedule(tasks)

    assert "Morning walk" in result.explanation
    assert "Bath time"    in result.explanation