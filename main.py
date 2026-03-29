"""
main.py — Demo script for PawPal+.

Verifies that the Owner / Pet / Task / Scheduler object model
is wired correctly by building a small example and printing a summary.
"""

from pawpal_system import Owner, Pet, Task, Scheduler


def main() -> None:
    # --- Build the object model ---
    owner = Owner(name="Jordan")

    mochi = Pet(name="Mochi", species="cat")
    mochi.add_task(Task(description="Morning feeding", time="07:30", frequency="daily"))
    mochi.add_task(Task(description="Medication",      time="08:00", frequency="daily"))

    buddy = Pet(name="Buddy", species="dog")
    buddy.add_task(Task(description="Morning walk",    time="07:00", frequency="daily"))
    buddy.add_task(Task(description="Evening walk",    time="18:00", frequency="daily"))
    buddy.add_task(Task(description="Vet appointment", time="10:00", frequency="once"))

    owner.add_pet(mochi)
    owner.add_pet(buddy)

    scheduler = Scheduler(owner=owner)

    # --- Print summary ---
    print(f"Owner : {owner.name}")
    print(f"Pets  : {len(owner.pets)}")
    for pet in owner.pets:
        print(f"\n  {pet.name} ({pet.species}) — {len(pet.get_tasks())} task(s)")
        for task in pet.get_tasks():
            status = "done" if task.is_complete else "pending"
            print(f"    [{status}] {task.time}  {task.description}  ({task.frequency})")

    all_tasks = scheduler.get_schedule()
    print(f"\nTotal tasks visible to Scheduler : {len(all_tasks)}")


if __name__ == "__main__":
    main()
