
import streamlit as st
import importlib
import html
import tasks


# --------------------------------------------------
# RELOAD TASKS.PY
# --------------------------------------------------

# Ensures the planner loads the latest saved task definitions.
importlib.reload(tasks)

DAY_1_TASKS = tasks.DAY_1_TASKS
EXTRA_TASKS = tasks.EXTRA_TASKS


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Today's plan · FlexiTarget",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# --------------------------------------------------
# SIGN-IN CHECK
# --------------------------------------------------

if not st.session_state.get("signed_in") or not st.session_state.get("student"):

    st.warning("Complete sign in and student setup first.")

    if st.button("Go to sign in"):
        st.switch_page("app.py")

    st.stop()


# --------------------------------------------------
# CUSTOM STYLING
# --------------------------------------------------

st.markdown("""
<style>

.stApp {
    background:
        radial-gradient(
            circle at 50% 0%,
            rgba(47,124,255,.08),
            transparent 36%
        ),
        #111317;
    color: #f3f6fa;
}

.block-container {
    max-width: 850px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

[data-testid="stHeader"],
[data-testid="stToolbar"] {
    visibility: hidden;
}

div.stButton > button {
    width: 100%;
    min-height: 45px;
    border-radius: 12px;
    background: #1d232b;
    color: #eaf0f7;
    border: 1px solid #34404d;
    font-weight: 700;
}

div.stButton > button[kind="primary"] {
    background: #2f7cff;
    border-color: #2f7cff;
    color: white;
}

div[data-testid="stTextArea"] textarea,
div[data-testid="stNumberInput"] input {
    background: #15191f !important;
    color: #f3f6fa !important;
    border: 1px solid #303743 !important;
    border-radius: 11px !important;
}

a[data-testid="stLinkButton"] {
    border-radius: 9px;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# URL CLEANING FUNCTION
# --------------------------------------------------

def clean_resource_url(raw_url):

    if not raw_url:
        return None

    url = str(raw_url).strip()

    # Remove accidental backslashes from copied URLs.
    url = url.replace("\\", "")

    # Remove accidental surrounding quotation marks.
    url = url.strip('"').strip("'")

    # Fix URLs that have only one slash after the colon.
    if url.startswith("https:/") and not url.startswith("https://"):
        url = url.replace("https:/", "https://", 1)

    if url.startswith("http:/") and not url.startswith("http://"):
        url = url.replace("http:/", "http://", 1)

    # Add HTTPS if a URL was entered without a scheme.
    if url.startswith("www."):
        url = "https://" + url

    if not url.startswith(("https://", "http://")):
        return None

    return url


# --------------------------------------------------
# STUDENT INFORMATION
# --------------------------------------------------

student = st.session_state.student

day = st.session_state.get("day_number", 1)

if "available_hours_today" not in st.session_state:
    st.session_state.available_hours_today = int(
        student.get("daily_hours", 6)
    )

if "extra_tasks" not in st.session_state:
    st.session_state.extra_tasks = []

if "task_checks" not in st.session_state:
    st.session_state.task_checks = {}


# --------------------------------------------------
# PAGE HEADING
# --------------------------------------------------

st.title(f"Today's plan, {student['name']}")

goal_caption = f"Day {day} · Goal: {student['goal_type']}"

if (
    student.get("target") is not None
    and student.get("goal_type") == "I want to score X marks"
):
    goal_caption += f" ({student['target']}%)"

st.caption(goal_caption)

st.markdown(
    f"### {st.session_state.available_hours_today} study hours available today"
)


# --------------------------------------------------
# CHANGE AVAILABLE HOURS
# --------------------------------------------------

with st.expander("Change today's available hours"):

    new_hours = st.slider(
        "How much time can you study today?",
        min_value=1,
        max_value=12,
        value=int(st.session_state.available_hours_today),
        key="hours_adjust"
    )

    if st.button("Update my plan"):
        st.session_state.available_hours_today = new_hours
        st.rerun()


# --------------------------------------------------
# SELECT TASKS
# --------------------------------------------------

all_tasks = DAY_1_TASKS + st.session_state.extra_tasks

capacity = st.session_state.available_hours_today * 60

selected = []
used = 0

# Keep tasks in their original order.
for task in all_tasks:

    duration = int(task.get("minutes", 0))

    if used + duration <= capacity:
        selected.append(task)
        used += duration


# --------------------------------------------------
# DISPLAY TASKS
# --------------------------------------------------

st.markdown("### Your to-dos")

st.caption(
    "Tick each task when you finish it. "
    "Open its learning resource when a link is available."
)

for i, task in enumerate(selected):

    task_key = f"day_{day}_task_{i}"

    with st.container(border=True):

        # Task checkbox.
        checked = st.checkbox(
            (
                f"{task['subject']}: "
                f"{task['title']} "
                f"· {task['minutes']} min"
            ),
            key=task_key
        )

        # Get and clean the URL from tasks.py.
        resource_url = clean_resource_url(task.get("url"))

        # Display a clickable button only when a valid URL exists.
        if resource_url:

            st.link_button(
                "Open learning resource ↗",
                resource_url,
                use_container_width=False
            )

    st.session_state.task_checks[task_key] = checked


# --------------------------------------------------
# STUDY TIME SUMMARY
# --------------------------------------------------

st.markdown("---")

total_minutes = sum(
    int(task.get("minutes", 0))
    for task in selected
)

completed_count = sum(
    bool(st.session_state.task_checks.get(
        f"day_{day}_task_{i}", False
    ))
    for i in range(len(selected))
)

col1, col2, col3 = st.columns(3)

col1.metric("Tasks shown", len(selected))
col2.metric("Study time", f"{total_minutes // 60}h {total_minutes % 60}m")
col3.metric("Completed", f"{completed_count}/{len(selected)}")


# --------------------------------------------------
# MORE TASKS
# --------------------------------------------------

if st.button("I have more time, give me more to-dos"):

    if EXTRA_TASKS:

        next_index = (
            len(st.session_state.extra_tasks) % len(EXTRA_TASKS)
        )

        next_task = EXTRA_TASKS[next_index].copy()

        st.session_state.extra_tasks.append(next_task)

        st.rerun()

    else:
        st.info("No additional tasks have been added yet.")


# --------------------------------------------------
# END-OF-DAY REFLECTION
# --------------------------------------------------

st.markdown("---")

st.markdown("### End-of-day reflection")

reflection = st.text_area(
    "What did you complete? What was difficult? What mistakes did you make?",
    placeholder=(
        "Example: I solved 15 questions. "
        "I got 10 correct and made mistakes in 5. "
        "I need to revise this topic."
    ),
    height=130,
    key=f"reflection_day_{day}"
)


# --------------------------------------------------
# SUBMIT DAILY PROGRESS
# --------------------------------------------------

if st.button("Submit today's progress", type="primary"):

    completed = sum(
        bool(value)
        for key, value in st.session_state.task_checks.items()
        if key.startswith(f"day_{day}_")
    )

    total = len(selected)

    record = {
        "day": day,
        "available_hours": st.session_state.available_hours_today,
        "completed": completed,
        "total": total,
        "reflection": reflection
    }

    st.session_state.setdefault(
        "progress_history", []
    ).append(record)

    st.session_state.day_number = day + 1

    st.session_state.available_hours_today = int(
        student.get("daily_hours", 6)
    )

    st.session_state.extra_tasks = []
    st.session_state.task_checks = {}

    st.success(
        f"Progress submitted: {completed} of {total} tasks completed."
    )

    st.balloons()


# --------------------------------------------------
# SAVED PROGRESS
# --------------------------------------------------

with st.expander("View my saved progress in this session"):

    history = st.session_state.get("progress_history", [])

    if history:

        for item in reversed(history):

            st.write(
                f"Day {item['day']}: "
                f"{item['completed']}/{item['total']} tasks · "
                f"{item['available_hours']} hours"
            )

            if item["reflection"]:
                st.caption(item["reflection"])

    else:
        st.caption("Your submitted days will appear here.")


# --------------------------------------------------
# TROUBLESHOOTING: RESOURCE LINKS
# --------------------------------------------------

with st.expander("Technical check: task resources"):

    st.caption(f"Currently loading tasks from: {tasks.__file__}")

    for i, task in enumerate(DAY_1_TASKS, start=1):

        raw_url = task.get("url", "")
        cleaned_url = clean_resource_url(raw_url)

        st.write(f"Task {i}: {task['subject']}")

        if cleaned_url:
            st.write(f"Resource: {cleaned_url}")
        else:
            st.caption("No resource URL is assigned.")


# --------------------------------------------------
# NAVIGATION
# --------------------------------------------------

if st.button("Edit student information"):
    st.switch_page("pages/student_info.py")

if st.button("Sign out"):
    st.session_state.clear()
    st.rerun()
