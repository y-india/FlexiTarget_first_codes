import streamlit as st
from tasks import DAY_1_TASKS, EXTRA_TASKS

st.set_page_config(page_title="Today's plan · FlexiTarget", page_icon="🎯", layout="centered", initial_sidebar_state="collapsed")
if not st.session_state.get("signed_in") or not st.session_state.get("student"):
    st.warning("Complete sign in and student setup first.")
    if st.button("Go to sign in"): st.switch_page("app.py")
    st.stop()

st.markdown("""
<style>
.stApp { background:radial-gradient(circle at 50% 0%,rgba(47,124,255,.08),transparent 36%),#111317; color:#f3f6fa; }
.block-container { max-width:850px; padding-top:2rem; padding-bottom:3rem; }
[data-testid="stHeader"],[data-testid="stToolbar"] {visibility:hidden}
.task {background:rgba(92,101,116,.10);border:1px solid #2d3440;border-radius:15px;padding:1rem;margin:.6rem 0}
div.stButton>button {width:100%;min-height:45px;border-radius:12px;background:#1d232b;color:#eaf0f7;border:1px solid #34404d;font-weight:700}
div.stButton>button[kind="primary"] {background:#2f7cff;border-color:#2f7cff;color:white}
div[data-testid="stTextArea"] textarea,div[data-testid="stNumberInput"] input {background:#15191f!important;color:#f3f6fa!important;border:1px solid #303743!important;border-radius:11px!important}
</style>
""", unsafe_allow_html=True)

student = st.session_state.student
day = st.session_state.get("day_number", 1)
if "available_hours_today" not in st.session_state:
    st.session_state.available_hours_today = student["daily_hours"]
if "extra_tasks" not in st.session_state:
    st.session_state.extra_tasks = []
if "task_checks" not in st.session_state:
    st.session_state.task_checks = {}

st.title(f"Today's plan, {student['name']}")
st.caption(f"Day {day} · Goal: {student['goal_type']}" + (f" ({student['target']}%)" if student["goal_type"] == "I want to score X marks" else ""))

st.markdown(f"### {st.session_state.available_hours_today} study hours available today")
with st.expander("Change today's available hours"):
    new_hours = st.slider("How much time can you study today?", 1, 12, int(st.session_state.available_hours_today), key="hours_adjust")
    if st.button("Update my plan"):
        st.session_state.available_hours_today = new_hours
        st.rerun()

# TASK EDITING: change tasks.py to edit the starter tasks.
# The prototype scales the number of suggested tasks to the available time.
all_tasks = DAY_1_TASKS + st.session_state.extra_tasks
capacity = st.session_state.available_hours_today * 60
selected, used = [], 0
for task in all_tasks:
    if used + task["minutes"] <= capacity:
        selected.append(task)
        used += task["minutes"]

st.markdown("### Your to-dos")
st.caption("Tick each task when you finish it. Open a resource link where one is provided.")
for i, task in enumerate(selected):
    task_key = f"day_{day}_task_{i}"
    checked = st.checkbox(f"{task['subject']}: {task['title']}  ·  {task['minutes']} min", key=task_key)
    if task.get("url"):
        st.markdown(f"[Open learning resource]({task['url']})")
    st.session_state.task_checks[task_key] = checked

if st.button("I have more time, give me more to-dos"):
    next_task = EXTRA_TASKS[len(st.session_state.extra_tasks) % len(EXTRA_TASKS)].copy()
    st.session_state.extra_tasks.append(next_task)
    st.rerun()

st.markdown("---")
st.markdown("### End-of-day reflection")
reflection = st.text_area(
    "What did you complete? What was difficult? What mistakes did you make?",
    placeholder="Example: I solved 15 questions. I got 10 correct and made mistakes in 5. I need to revise this topic.",
    height=130,
    key=f"reflection_day_{day}"
)

if st.button("Submit today's progress", type="primary"):
    completed = sum(bool(v) for k, v in st.session_state.task_checks.items() if k.startswith(f"day_{day}_"))
    total = len(selected)
    record = {
        "day": day, "available_hours": st.session_state.available_hours_today,
        "completed": completed, "total": total, "reflection": reflection
    }
    st.session_state.setdefault("progress_history", []).append(record)
    st.session_state.day_number = day + 1
    st.session_state.available_hours_today = student["daily_hours"]
    st.session_state.extra_tasks = []
    st.session_state.task_checks = {}
    st.success(f"Progress submitted: {completed} of {total} tasks completed. Your next session will start with an updated day.")
    st.balloons()

with st.expander("View my saved progress in this session"):
    history = st.session_state.get("progress_history", [])
    if history:
        for item in reversed(history):
            st.write(f"Day {item['day']}: {item['completed']}/{item['total']} tasks · {item['available_hours']} hours")
            if item["reflection"]:
                st.caption(item["reflection"])
    else:
        st.caption("Your submitted days will appear here.")

if st.button("Edit student information"):
    st.switch_page("pages/student_info.py")
if st.button("Sign out"):
    st.session_state.clear()
    st.rerun()
