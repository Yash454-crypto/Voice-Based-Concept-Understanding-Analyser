"""
app.py
========
Streamlit application entry point for the
Voice-Based Concept Understanding Analyser.

Run with:
    streamlit run app.py

This file initializes:
    - Page config (title, icon, layout)
    - Session state defaults
    - Sidebar navigation
    - Global CSS styling
    - Routing to individual page modules
"""

import streamlit as st

# ---------------------------------------------------------
# 1. Page configuration (must be the first Streamlit call)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Voice-Based Concept Understanding Analyser",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# 2. Global session state initialization
# ---------------------------------------------------------
DEFAULT_STATE = {
    "student_name": "",
    "student_id": None,
    "current_session_id": None,
    "audio_file_path": None,
    "transcript_text": "",
    "analysis_results": None,
    "history": [],          # list of past session summaries
}

for key, default_value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = default_value

# ---------------------------------------------------------
# 3. Global CSS styling
# ---------------------------------------------------------
def load_custom_css():
    st.markdown(
        """
        <style>
        .main-header {
            font-size: 2.2rem;
            font-weight: 700;
            color: #1a73e8;
            padding-bottom: 0.2rem;
        }
        .sub-header {
            font-size: 1rem;
            color: #5f6368;
            margin-bottom: 1.5rem;
        }
        .metric-card {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 1rem;
            border: 1px solid #e0e0e0;
        }
        section[data-testid="stSidebar"] {
            background-color: #f1f5f9;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


load_custom_css()

# ---------------------------------------------------------
# 4. Sidebar — navigation & student info
# ---------------------------------------------------------
def render_sidebar():
    with st.sidebar:
        st.markdown("## 🎙️ Concept Analyser")
        st.caption("Voice-based understanding assessment")
        st.divider()

        page = st.radio(
            "Navigate",
            options=[
                "🏠 Home",
                "🎤 Record & Analyse",
                "📊 Results",
                "📁 History",
                "⚙️ Settings",
            ],
            label_visibility="collapsed",
        )

        st.divider()
        st.text_input("Student name", key="student_name", placeholder="Enter your name")

        st.divider()
        st.caption("Version 0.1.0")

    return page


# ---------------------------------------------------------
# 5. Page renderers
#    (kept inline here for a single-file starter;
#     move each to /pages or src/ui/ as the app grows)
# ---------------------------------------------------------
def page_home():
    st.markdown('<div class="main-header">Voice-Based Concept Understanding Analyser</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Speak your understanding of a concept — '
        'we transcribe, analyse, and score it.</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Sessions Completed", len(st.session_state["history"]))
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        avg_score = (
            sum(h.get("score", 0) for h in st.session_state["history"]) / len(st.session_state["history"])
            if st.session_state["history"] else 0
        )
        st.metric("Average Understanding Score", f"{avg_score:.1f}%")
        st.markdown("</div>", unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Current Student", st.session_state["student_name"] or "Not set")
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.info("👈 Use the sidebar to start a new recording session or view past results.")


def page_record_analyse():
    st.markdown("## 🎤 Record & Analyse")
    st.caption("Select a topic/concept, then record or upload your spoken explanation.")

    topic = st.selectbox("Select a topic", ["Photosynthesis", "Newton's Laws", "Supply & Demand", "Custom..."])
    if topic == "Custom...":
        topic = st.text_input("Enter custom topic name")

    st.write("")
    tab_record, tab_upload = st.tabs(["🎙️ Record Audio", "📤 Upload Audio File"])

    with tab_record:
        st.warning("Live mic recording requires a custom component (e.g., `streamlit-webrtc` or `audio_recorder_streamlit`). Placeholder below.")
        st.button("● Start Recording", disabled=True, help="Wire up audio recording backend here")

    with tab_upload:
        audio_file = st.file_uploader("Upload a .wav or .mp3 file", type=["wav", "mp3", "m4a"])
        if audio_file is not None:
            st.session_state["audio_file_path"] = audio_file.name
            st.audio(audio_file)
            st.success(f"Loaded: {audio_file.name}")

    st.write("")
    if st.button("🚀 Run Analysis", type="primary", use_container_width=True):
        if not st.session_state["audio_file_path"]:
            st.error("Please upload or record audio first.")
        else:
            with st.spinner("Transcribing and analysing concept understanding..."):
                # TODO: call src.speech_to_text.transcriber.transcribe_audio(...)
                # TODO: call src.nlp.concept_matcher.match_concepts(...)
                # TODO: call src.analysis.scorer.compute_understanding_score(...)
                st.session_state["transcript_text"] = "[Transcript placeholder — wire up STT module]"
                st.session_state["analysis_results"] = {
                    "topic": topic,
                    "score": 0,
                    "matched_keywords": [],
                    "missing_keywords": [],
                }
            st.success("Analysis complete. Check the Results page.")


def page_results():
    st.markdown("## 📊 Results")
    results = st.session_state["analysis_results"]

    if not results:
        st.info("No analysis yet. Go to **Record & Analyse** first.")
        return

    st.subheader(f"Topic: {results['topic']}")
    st.progress(results["score"] / 100 if results["score"] else 0)
    st.metric("Understanding Score", f"{results['score']}%")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**✅ Matched Concepts**")
        st.write(results["matched_keywords"] or "—")
    with col2:
        st.markdown("**❌ Missing Concepts**")
        st.write(results["missing_keywords"] or "—")

    with st.expander("View full transcript"):
        st.write(st.session_state["transcript_text"])


def page_history():
    st.markdown("## 📁 Session History")
    if not st.session_state["history"]:
        st.info("No past sessions yet.")
        return
    st.dataframe(st.session_state["history"], use_container_width=True)


def page_settings():
    st.markdown("## ⚙️ Settings")
    st.text_input("Database URL", value="sqlite:///data/app.db", disabled=True)
    st.selectbox("Whisper model size", ["tiny", "base", "small", "medium", "large"], index=1)
    st.slider("Understanding score pass threshold (%)", 0, 100, 60)
    st.caption("Settings persistence not yet wired up — connect to src/utils/config.py")


# ---------------------------------------------------------
# 6. Router
# ---------------------------------------------------------
PAGES = {
    "🏠 Home": page_home,
    "🎤 Record & Analyse": page_record_analyse,
    "📊 Results": page_results,
    "📁 History": page_history,
    "⚙️ Settings": page_settings,
}


def main():
    selected_page = render_sidebar()
    PAGES[selected_page]()


if __name__ == "__main__":
    main()