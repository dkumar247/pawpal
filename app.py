import streamlit as st
from scheduler import Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    if not task_title.strip():
        st.error("Task title cannot be blank. Please enter a name for the task.")
    else:
        st.session_state.tasks.append(
            {"title": task_title.strip(), "duration_minutes": int(duration), "priority": priority}
        )

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")

time_budget = st.number_input(
    "Time budget for today (minutes)", min_value=1, max_value=1440, value=60
)

if st.button("Generate schedule"):
    if not owner_name.strip():
        st.error("Owner name cannot be blank.")
    elif not pet_name.strip():
        st.error("Pet name cannot be blank.")
    elif not st.session_state.tasks:
        st.warning("Add at least one task before generating a schedule.")
    elif int(time_budget) < 1:
        st.error("Time budget must be at least 1 minute.")
    else:
        try:
            tasks = [
                Task(
                    title=t["title"],
                    duration=t["duration_minutes"],
                    priority=t["priority"],
                )
                for t in st.session_state.tasks
            ]
            result = Scheduler(time_budget_minutes=int(time_budget)).schedule(tasks)
        except (ValueError, KeyError) as exc:
            st.error(f"Could not build schedule: {exc}")
            st.stop()
        except Exception as exc:
            st.error(f"Unexpected error — this may be a bug: {exc}")
            st.stop()

        st.markdown("#### Scheduled tasks")
        if result.selected:
            st.table(
                [
                    {
                        "Task": t.title,
                        "Duration (min)": t.duration,
                        "Priority": t.priority.value,
                    }
                    for t in result.selected
                ]
            )
        else:
            st.info(
                "No tasks fit within the time budget. "
                "Try increasing the time budget or reducing task durations."
            )

        if result.skipped:
            st.markdown("#### Skipped tasks")
            st.table(
                [
                    {
                        "Task": t.title,
                        "Duration (min)": t.duration,
                        "Priority": t.priority.value,
                    }
                    for t in result.skipped
                ]
            )

        st.markdown("#### Explanation")
        st.code(result.explanation, language=None)
