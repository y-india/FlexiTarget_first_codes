
import streamlit as st


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Student details · FlexiTarget",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="collapsed"
)

if st.button("What is FlexiTarget?"):
    st.switch_page("pages/info.py") 

# --------------------------------------------------
# SIGN-IN CHECK
# --------------------------------------------------

if not st.session_state.get("signed_in"):
    st.warning("Please sign in first.")

    if st.button("Go to sign in"):
        st.switch_page("app.py")

    st.stop()


# --------------------------------------------------
# SUBJECT OPTIONS
# --------------------------------------------------

SUBJECTS = {
    "Science": [
        "Physics",
        "Chemistry",
        "English Core",
        "Mathematics",
        "Biology",
        "Computer Science",
        "Informatics Practices",
        "Biotechnology",
        "Engineering Graphics",
        "Physical Education",
        "Psychology",
        "Fine Arts"
    ],

    "Commerce": [
        "Accountancy",
        "Business Studies",
        "Economics",
        "English Core",
        "Mathematics",
        "Applied Mathematics",
        "Entrepreneurship",
        "Informatics Practices",
        "Physical Education",
        "Legal Studies",
        "Home Science"
    ],

    "Arts (Humanities)": [
        "English Core",
        "History",
        "Political Science",
        "Geography",
        "Economics",
        "Sociology",
        "Psychology",
        "Philosophy",
        "Mathematics",
        "Fine Arts",
        "Music",
        "Dance",
        "Home Science",
        "Physical Education"
    ]
}


# --------------------------------------------------
# LOAD PREVIOUSLY SAVED STUDENT INFORMATION
# --------------------------------------------------

saved = st.session_state.get("student", {})

saved_stream = saved.get("stream", "Commerce")

if saved_stream not in SUBJECTS:
    saved_stream = "Commerce"

saved_goal = saved.get(
    "goal_type",
    "Complete my syllabus"
)

if saved_goal not in [
    "Complete my syllabus",
    "I want to score X marks"
]:
    saved_goal = "Complete my syllabus"


# Convert saved subjects into a list if necessary.
saved_subjects = saved.get("subjects", [])

if isinstance(saved_subjects, str):
    saved_subjects = [
        subject.strip()
        for subject in saved_subjects.split(",")
        if subject.strip()
    ]


# Convert saved weak subjects into a list if necessary.
saved_weak_subjects = saved.get("weak_subjects", [])

if isinstance(saved_weak_subjects, str):
    saved_weak_subjects = [
        subject.strip()
        for subject in saved_weak_subjects.split(",")
        if subject.strip()
    ]


# Safely load the saved target.
try:
    saved_target = int(saved.get("target") or 90)
    saved_target = max(1, min(100, saved_target))
except (TypeError, ValueError):
    saved_target = 90


# Safely load daily study hours.
try:
    saved_hours = int(saved.get("daily_hours", 4))
    saved_hours = max(1, min(12, saved_hours))
except (TypeError, ValueError):
    saved_hours = 4


# --------------------------------------------------
# INITIALIZE SESSION STATE
# --------------------------------------------------

defaults = {
    "profile_name": saved.get("name", ""),
    "profile_stream": saved_stream,
    "profile_subjects": [
        subject for subject in saved_subjects
        if subject in SUBJECTS[saved_stream]
    ],
    "profile_last_exam": saved.get("last_exam", ""),
    "profile_goal": saved_goal,
    "target_saved": saved_target,
    "profile_daily_hours": saved_hours,
    "profile_weak_subjects": saved_weak_subjects,
    "profile_current_status": saved.get("current_status", "")
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# Remember the target even if the target input gets hidden.
def remember_target():
    st.session_state["target_saved"] = int(
        st.session_state["profile_target_input"]
    )


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
    max-width: 820px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

[data-testid="stHeader"],
[data-testid="stToolbar"] {
    visibility: hidden;
}

div.stButton > button {
    width: 100%;
    min-height: 46px;
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

div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stNumberInput"] input {
    background: #15191f !important;
    color: #f3f6fa !important;
    border: 1px solid #303743 !important;
    border-radius: 11px !important;
}

div[data-testid="stMultiSelect"] {
    color: #f3f6fa;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# PAGE HEADING
# --------------------------------------------------

st.title("Set up your study profile")

st.caption(
    "Tell FlexiTarget about your subjects, goals and study routine. "
    "Your answers will help create your daily study plan."
)


# --------------------------------------------------
# STUDENT NAME
# --------------------------------------------------

st.subheader("Your details")

name = st.text_input(
    "What should we call you?",
    key="profile_name",
    placeholder="Enter your name"
)


# --------------------------------------------------
# STREAM SELECTION
# --------------------------------------------------

st.subheader("Your stream")

stream = st.radio(
    "Select your Class 12 stream",
    options=[
        "Science",
        "Commerce",
        "Arts (Humanities)"
    ],
    key="profile_stream"
)


# --------------------------------------------------
# SUBJECT SELECTION
# --------------------------------------------------

st.subheader("Your subjects")

subject_options = SUBJECTS[stream]

# Remove subjects that do not belong to the newly selected stream.
st.session_state["profile_subjects"] = [
    subject
    for subject in st.session_state["profile_subjects"]
    if subject in subject_options
]

selected_subjects = st.multiselect(
    "Select all the subjects you study",
    options=subject_options,
    key="profile_subjects",
    placeholder="Choose your subjects..."
)


# --------------------------------------------------
# LAST EXAM PERFORMANCE
# --------------------------------------------------

st.subheader("Your previous performance")

last_exam = st.text_input(
    "Last exam performance",
    key="profile_last_exam",
    placeholder="Example: 45% in half-yearly examinations"
)


# --------------------------------------------------
# ACADEMIC GOAL
# --------------------------------------------------

st.subheader("Your academic goal")

goal_type = st.radio(
    "What do you want to achieve?",
    options=[
        "Complete my syllabus",
        "I want to score X marks"
    ],
    key="profile_goal"
)


# Show this question immediately when the second option is selected.
if goal_type == "I want to score X marks":

    if "profile_target_input" not in st.session_state:
        st.session_state["profile_target_input"] = (
            st.session_state["target_saved"]
        )

    target = st.number_input(
        "What is that X%?",
        min_value=1,
        max_value=100,
        step=1,
        key="profile_target_input",
        on_change=remember_target
    )

else:
    target = None


# --------------------------------------------------
# DAILY STUDY AVAILABILITY
# --------------------------------------------------

st.subheader("Daily study availability")

daily_hours = st.slider(
    "How many hours can you study on a normal day?",
    min_value=1,
    max_value=12,
    key="profile_daily_hours"
)


# --------------------------------------------------
# WEAK SUBJECTS
# --------------------------------------------------

st.subheader("Your weak subjects")

# Remove weak subjects that are no longer selected.
st.session_state["profile_weak_subjects"] = [
    subject
    for subject in st.session_state["profile_weak_subjects"]
    if subject in selected_subjects
]

weak_subjects = st.multiselect(
    "Select the subjects you find difficult",
    options=selected_subjects,
    key="profile_weak_subjects",
    placeholder="Select your weak subjects...",
    disabled=(len(selected_subjects) == 0)
)

if not selected_subjects:
    st.caption("Select your subjects above to choose your weak subjects.")


# --------------------------------------------------
# CURRENT PREPARATION
# --------------------------------------------------

st.subheader("Current preparation")

current_status = st.text_area(
    "Tell us about your syllabus preparation",
    key="profile_current_status",
    placeholder=(
        "Example:\n"
        "Accountancy: 5 chapters completed, 3 pending.\n"
        "Economics: Most of Microeconomics completed.\n"
        "Mathematics: Struggling with Calculus."
    ),
    height=140
)


# --------------------------------------------------
# SUBMIT PROFILE
# --------------------------------------------------

st.markdown("---")

if st.button(
    "Create my study plan",
    type="primary",
    use_container_width=True
):

    if not name.strip():
        st.error("Please enter your name.")

    elif not selected_subjects:
        st.error("Please select at least one subject.")

    elif (
        goal_type == "I want to score X marks"
        and target is None
    ):
        st.error("Please enter your target percentage.")

    else:

        # Save the complete student profile.
        st.session_state.student = {
            "name": name.strip(),

            "stream": stream,

            "subjects": selected_subjects,

            "subjects_text": ", ".join(selected_subjects),

            "last_exam": last_exam.strip(),

            "goal_type": goal_type,

            "target": (
                int(target)
                if goal_type == "I want to score X marks"
                else None
            ),

            "daily_hours": int(daily_hours),

            "weak_subjects": weak_subjects,

            "weak_subjects_text": ", ".join(weak_subjects),

            "current_status": current_status.strip()
        }

        # Initialize the planner.
        st.session_state.day_number = 1
        st.session_state.available_hours_today = int(daily_hours)
        st.session_state.extra_tasks = []
        st.session_state.task_checks = {}

        # Open the planner page.
        st.switch_page("pages/planner.py")


# --------------------------------------------------
# BACK BUTTON
# --------------------------------------------------

if st.button("Back to sign in"):
    st.switch_page("app.py")
