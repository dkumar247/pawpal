# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

The initial design included five classes: `Pet`, `Owner`, `Task`, `Scheduler`, and `ScheduleResult`. `Pet` held species and care preferences; `Owner` held the owner's name and daily time availability. `Task` represented a single care activity with a title, duration, and priority. `Scheduler` selected tasks within a time budget; `ScheduleResult` carried the output.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

`Pet` and `Owner` were dropped during implementation. Neither class contributed any logic — the scheduler only needs a task list and a time budget. Owner and pet name are collected in the UI as display strings but have no effect on scheduling decisions. Retaining empty classes would have added indirection without value.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers two constraints: **priority** (high / medium / low) and **duration** relative to the remaining budget. Priority is primary; duration is secondary — a task is included only if it fits what remains.

Priority outranks duration because in a pet care context, missing a high-priority task (e.g., medication) is a worse outcome than leaving time unused.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

The scheduler uses a **greedy algorithm**: tasks are sorted by priority descending, with duration ascending as a tie-breaker, then selected in order until the budget is exhausted.

This is a deliberate simplification. The tradeoff is that greedy selection can miss more efficient packings — two medium-priority 20-minute tasks might both fit where one high-priority 45-minute task leaves wasted time and excludes both. An optimal solution would require dynamic programming (a 0/1 knapsack variant), which is substantially more complex. For a single-day planner with a small task list, the greedy approach is sufficient and produces intuitive results.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

AI was used throughout: generating the initial `scheduler.py` structure, writing the pytest suite, wiring the scheduler into the Streamlit UI, and adding edge-case handling in `app.py`. The most effective prompts were specific and constrained — for example, requesting edge-case handling with an explicit "do not refactor unrelated code" instruction produced focused changes rather than broad rewrites.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

When AI broadened the exception handler from `except (ValueError, KeyError)` to `except Exception`, the suggestion was not accepted as-is. The concern was that catching all exceptions would silently mask genuine bugs during development. The resolution was to retain the specific types for expected errors and add a separate broad catch with an explicit "this may be a bug" message — preserving crash prevention without hiding unexpected failures. That decision required reasoning about the *intent* of each exception type, not just the immediate effect of the change.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

Thirteen pytest tests cover five areas:

- **Priority selection** — high beats medium and low; all three priorities ordered correctly when all tasks fit
- **Tasks that don't fit** — an over-budget task is skipped; all tasks too long results in empty `selected`
- **Budget invariant** — `total_time` never exceeds budget; `total_time` equals the sum of selected durations
- **Determinism** — identical inputs produce identical outputs; input list order does not affect task selection
- **Edge cases** — empty task list, task that exactly fills the budget, explanation references both selected and skipped tasks

All tests target `scheduler.py` directly with no Streamlit dependency, keeping them fast and ensuring the backend is independently verifiable.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

Confidence is high for the core scheduling contract: priority ordering, budget enforcement, and determinism. The main gap is the UI layer — no automated tests verify that `app.py` renders the correct messages for each edge case (blank name, all tasks too long, etc.), which were validated manually.

Edge cases to test next: tasks with identical priority and duration (sort stability), a budget of exactly 1 minute, and a large task list to check for performance regression.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

The separation between backend (`scheduler.py`) and UI (`app.py`) was the strongest aspect of the design. Because `Scheduler` and `Task` have no dependency on Streamlit, they can be tested in isolation and reasoned about independently. The clean interface — a list of `Task` objects and a budget in, a `ScheduleResult` out — made the UI layer straightforward to build.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

In a future iteration:
- **Add time-of-day scheduling.** The current output is a ranked list, not a time-blocked plan. Assigning start times would make the schedule directly actionable (e.g., "Walk at 8:00am, feed at 8:20am").
- **Derive priority from pet and owner data.** Currently priority is set manually. A pet with a medication flag could automatically elevate relevant tasks to high priority without user input.
- **Replace greedy selection with knapsack DP** where maximising total scheduled time matters more than strict priority ordering.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

Evaluating AI suggestions requires domain reasoning, not just syntactic review. The `except Exception` change looked correct on the surface — it prevented crashes — but understanding *why* the original exception types were specific was what revealed the problem. Accepting the change without that reasoning would have made future bugs harder to diagnose. Effective AI collaboration means evaluating intent, not just outcome.