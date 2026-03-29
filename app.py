import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    "A pet care scheduling assistant. Add tasks for your pet "
    "and get a sorted, conflict-checked daily schedule."
)

st.divider()

st.subheader("Owner & Pet")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

st.markdown("### Tasks")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "editing_index" not in st.session_state:
    st.session_state.editing_index = None


def valid_time(t: str) -> bool:
    """Return True if t is a valid HH:MM string."""
    parts = t.strip().split(":")
    if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
        return False
    return 0 <= int(parts[0]) <= 23 and 0 <= int(parts[1]) <= 59


col1, col2, col3 = st.columns(3)
with col1:
    task_desc = st.text_input("Description", value="Morning walk")
with col2:
    task_time = st.text_input("Time (HH:MM)", value="07:00")
with col3:
    task_freq = st.selectbox("Frequency", ["daily", "weekly", "once"])

if st.button("Add task"):
    if not task_desc.strip():
        st.error("Description cannot be blank.")
    elif not valid_time(task_time):
        st.error("Time must be in HH:MM format (e.g. 07:30).")
    else:
        st.session_state.tasks.append(
            Task(description=task_desc.strip(), time=task_time.strip(), frequency=task_freq)
        )

if st.session_state.tasks:
    st.write("Current tasks:")
    for i, task in enumerate(st.session_state.tasks):
        if st.session_state.editing_index == i:
            ecol1, ecol2, ecol3 = st.columns(3)
            new_desc = ecol1.text_input("Description", value=task.description, key=f"edit_desc_{i}")
            new_time = ecol2.text_input("Time (HH:MM)", value=task.time, key=f"edit_time_{i}")
            new_freq = ecol3.selectbox(
                "Frequency", ["daily", "weekly", "once"],
                index=["daily", "weekly", "once"].index(task.frequency),
                key=f"edit_freq_{i}",
            )
            scol1, scol2 = st.columns([1, 5])
            if scol1.button("Save", key=f"save_{i}"):
                if not new_desc.strip():
                    st.error("Description cannot be blank.")
                elif not valid_time(new_time):
                    st.error("Time must be in HH:MM format (e.g. 07:30).")
                else:
                    st.session_state.tasks[i] = Task(
                        description=new_desc.strip(),
                        time=new_time.strip(),
                        frequency=new_freq,
                    )
                    st.session_state.editing_index = None
                    st.rerun()
            if scol2.button("Cancel", key=f"cancel_{i}"):
                st.session_state.editing_index = None
                st.rerun()
        else:
            col_desc, col_time, col_freq, col_edit, col_remove = st.columns([4, 2, 2, 1, 1])
            col_desc.write(task.description)
            col_time.write(task.time)
            col_freq.write(task.frequency)
            if col_edit.button("Edit", key=f"edit_{i}"):
                st.session_state.editing_index = i
                st.rerun()
            if col_remove.button("Remove", key=f"remove_{i}"):
                st.session_state.tasks.pop(i)
                st.session_state.editing_index = None
                st.rerun()
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Today's Schedule")

if st.button("Generate schedule"):
    if not owner_name.strip():
        st.error("Owner name cannot be blank.")
    elif not pet_name.strip():
        st.error("Pet name cannot be blank.")
    elif not st.session_state.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        try:
            pet = Pet(name=pet_name.strip(), species=species)
            for t in st.session_state.tasks:
                pet.add_task(t)
            owner = Owner(name=owner_name.strip())
            owner.add_pet(pet)
            scheduler = Scheduler(owner=owner)

            sorted_tasks = scheduler.sort_by_time()
            conflicts = scheduler.detect_conflicts()
        except (ValueError, KeyError) as exc:
            st.error(f"Could not build schedule: {exc}")
            st.stop()
        except Exception as exc:
            st.error(f"Unexpected error — this may be a bug: {exc}")
            st.stop()

        if conflicts:
            st.markdown("#### Conflicts detected")
            for warning in conflicts:
                st.warning(warning)

        st.markdown("#### Scheduled tasks (sorted by time)")
        if sorted_tasks:
            st.table([
                {
                    "Description": t.description,
                    "Time": t.time,
                    "Frequency": t.frequency,
                    "Status": "done" if t.is_complete else "pending",
                }
                for t in sorted_tasks
            ])
        else:
            st.info("No tasks to display.")
