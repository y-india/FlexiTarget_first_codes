import streamlit as st

st.set_page_config(page_title="FlexiTarget", page_icon="🎯", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
:root { --bg:#111317; --panel:#1a1e24; --border:#2d3440; --text:#f3f6fa; --muted:#949cab; --blue:#2f7cff; --blue2:#58a0ff; }
.stApp { background: radial-gradient(circle at 50% 0%, rgba(47,124,255,.09), transparent 36%), #111317; color:var(--text); }
.block-container { max-width:760px; padding-top:3rem; padding-bottom:3rem; }
[data-testid="stHeader"], [data-testid="stToolbar"] { background:transparent; visibility:hidden; }
.brand { text-align:center; color:var(--blue); font-size:2.5rem; font-weight:850; letter-spacing:-.05em; margin-bottom:.2rem; }
.tagline { text-align:center; color:var(--muted); margin-bottom:2.2rem; }
.panel { background:rgba(92,101,116,.10); border:1px solid rgba(148,156,171,.17); border-radius:20px; padding:1.3rem; margin-bottom:1rem; }
div.stButton > button { width:100%; min-height:47px; border-radius:12px; border:1px solid #34404d; background:#1d232b; color:#eaf0f7; font-weight:700; }
div.stButton > button[kind="primary"] { background:#2f7cff; border-color:#2f7cff; color:white; }
div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input, div[data-testid="stTextArea"] textarea { background:#15191f!important; color:#f3f6fa!important; border:1px solid #303743!important; border-radius:11px!important; }
.helper { color:#949cab; text-align:center; font-size:.82rem; }
</style>
""", unsafe_allow_html=True)

if "student" not in st.session_state:
    st.session_state.student = {}
if "signed_in" not in st.session_state:
    st.session_state.signed_in = False

st.markdown('<div class="brand">FlexiTarget</div><div class="tagline">A study plan that adjusts to your day.</div>', unsafe_allow_html=True)

st.markdown("---")

if st.button("What is FlexiTarget?", use_container_width=True):
    st.switch_page("pages/info.py")


if st.session_state.signed_in:
    st.markdown('<div class="panel"><h3>Welcome back</h3><p>Your study plan is ready when you are.</p></div>', unsafe_allow_html=True)
    if st.button("Open my study planner", type="primary"):
        st.switch_page("pages/student_info.py" if not st.session_state.student else "pages/planner.py")
    if st.button("Sign out"):
        st.session_state.clear()
        st.rerun()
else:
    st.markdown('<div class="panel"><h3>Sign in</h3><p style="color:#949cab">Enter your details to start your Class 12 study plan.</p></div>', unsafe_allow_html=True)
    with st.form("signin_form"):
        email = st.text_input("Email address", placeholder="you@example.com")
        password = st.text_input("Password", type="password", placeholder="Enter a password")
        submitted = st.form_submit_button("Sign in", type="primary", use_container_width=True)
    if submitted:
        if "@" not in email or "." not in email.split("@")[-1] or len(password) < 4:
            st.error("Enter a valid email address and a password of at least 4 characters.")
        else:
            # Prototype only: this is a session-based demo, not secure account authentication.
            st.session_state.signed_in = True
            st.session_state.email = email.strip()
            st.switch_page("pages/student_info.py")
    st.markdown('<div class="helper">New here? Enter an email and password to create a demo session.</div>', unsafe_allow_html=True)

st.caption("FlexiTarget · Class 12 study planner")
