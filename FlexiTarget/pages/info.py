import streamlit as st

st.set_page_config(page_title="About FlexiTarget", page_icon="🎯", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
.stApp {background:radial-gradient(circle at 50% 0%,rgba(47,124,255,.08),transparent 36%),#111317;color:#f3f6fa}
.block-container{max-width:850px;padding-top:2rem}
[data-testid="stHeader"],[data-testid="stToolbar"]{visibility:hidden}
.info-card{background:rgba(92,101,116,.10);border:1px solid rgba(148,156,171,.17);border-radius:18px;padding:1.2rem;margin:1rem 0}
div.stButton>button{width:100%;min-height:45px;border-radius:12px;background:#1d232b;color:#eaf0f7;border:1px solid #34404d;font-weight:700}
</style>
""", unsafe_allow_html=True)

st.title("FlexiTarget")
st.caption("A flexible daily study planner for Class 12 students.")

st.markdown("""
<div class="info-card">
<h3>What is FlexiTarget?</h3>
FlexiTarget helps Class 12 students turn their academic goals into manageable daily study tasks.
</div>
<div class="info-card">
<h3>How it works</h3>
1. Sign in and enter your student details.<br>
2. Choose one goal: complete your syllabus, or aim for a target score.<br>
3. Add your subjects, recent exam performance, weak subjects and usual study hours.<br>
4. Get a daily to-do plan with learning resources and practice tasks.<br>
5. Change your available hours when your day becomes busy or free.<br>
6. Submit your progress and explain what went well or what was difficult.
</div>
<div class="info-card">
<h3>Flexible by design</h3>
The plan should respond to the time you actually have. If you have more time, ask for extra tasks. If you have less time, reduce today's hours and work from the adjusted plan.
</div>
<div class="info-card">
<h3>Prototype note</h3>
This first version uses sample tasks and session-based progress. It does not yet use real account authentication, a permanent database, or an AI syllabus engine. Edit <code>tasks.py</code> to add your own tasks and resource links.
</div>
""", unsafe_allow_html=True)

if st.button("Back to FlexiTarget"):
    st.switch_page("app.py")
