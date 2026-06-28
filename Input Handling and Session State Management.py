"""
Input Handling & Session State Management Demo
-------------------------------------------------
Run with:  streamlit run session_state_app.py

Demonstrates:
- st.session_state basics (init, read, write, persist across reruns)
- Widget keys and how they auto-sync with session_state
- Callbacks (on_change / on_click) vs. reading state after rerun
- Input validation patterns
- Multi-step "wizard" form using session state to track step
- Dynamic/repeating input lists (add/remove rows)
- Debounced / "Apply" pattern to avoid excessive reruns
- Resetting state safely
"""

import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Session State & Input Handling", page_icon="🧠", layout="wide")

st.title("🧠 Input Handling & Session State Management")
st.caption("Reference patterns for managing user input and persistent state in Streamlit.")

# ============================================================================
# SECTION 1: Session State Basics
# ============================================================================
st.header("1. Session State Basics")

# Always initialize state defensively (only sets if not already present)
defaults = {
    "counter": 0,
    "username": "",
    "log": [],
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

col1, col2 = st.columns(2)
with col1:
    st.write("Current state values:")
    st.json({k: st.session_state[k] for k in defaults})

with col2:
    if st.button("Increment counter"):
        st.session_state.counter += 1
        st.session_state.log.append(f"Counter -> {st.session_state.counter}")
    if st.button("Reset section 1 state"):
        for key, value in defaults.items():
            st.session_state[key] = value
        st.rerun()

with st.expander("Action log"):
    st.write(st.session_state.log[-10:])

st.markdown("---")

# ============================================================================
# SECTION 2: Widget keys auto-sync with session_state
# ============================================================================
st.header("2. Widget Keys Bind Directly to session_state")
st.write(
    "Any widget given a `key=` automatically reads/writes `st.session_state[key]`. "
    "No manual wiring needed."
)

st.text_input("Type your name", key="username")
st.write(f"Live value from session_state: **{st.session_state.username or '(empty)'}**")

st.markdown("---")

# ============================================================================
# SECTION 3: Callbacks — on_change / on_click
# ============================================================================
st.header("3. Callbacks: on_change / on_click")


def handle_slider_change():
    # Callback fires BEFORE the rerun, with the new value already in session_state
    st.session_state.log.append(f"Slider changed -> {st.session_state.volume}")


st.slider("Volume", 0, 100, 50, key="volume", on_change=handle_slider_change)
st.caption("Each change is recorded in the action log above (callback fires pre-rerun).")

st.markdown("---")

# ============================================================================
# SECTION 4: Input validation pattern
# ============================================================================
st.header("4. Input Validation")

with st.form("validated_form"):
    email = st.text_input("Email address")
    age = st.number_input("Age", min_value=0, max_value=130, value=0)
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Validate & Submit")

if submitted:
    errors = []
    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(email_pattern, email or ""):
        errors.append("Email format looks invalid.")
    if age <= 0:
        errors.append("Age must be greater than 0.")
    if len(password) < 8:
        errors.append("Password must be at least 8 characters.")

    if errors:
        for e in errors:
            st.error(e)
    else:
        st.success("All inputs valid ✅")
        st.session_state.log.append("Form validated successfully")

st.markdown("---")

# ============================================================================
# SECTION 5: Multi-step wizard using session state
# ============================================================================
st.header("5. Multi-Step Wizard (Stateful Flow)")

if "wizard_step" not in st.session_state:
    st.session_state.wizard_step = 1
if "wizard_data" not in st.session_state:
    st.session_state.wizard_data = {}

TOTAL_STEPS = 3
progress = st.progress((st.session_state.wizard_step - 1) / TOTAL_STEPS)
st.write(f"Step {st.session_state.wizard_step} of {TOTAL_STEPS}")


def next_step():
    st.session_state.wizard_step = min(st.session_state.wizard_step + 1, TOTAL_STEPS)


def prev_step():
    st.session_state.wizard_step = max(st.session_state.wizard_step - 1, 1)


def reset_wizard():
    st.session_state.wizard_step = 1
    st.session_state.wizard_data = {}


if st.session_state.wizard_step == 1:
    st.subheader("Step 1: Basic Info")
    st.session_state.wizard_data["name"] = st.text_input(
        "Full name", value=st.session_state.wizard_data.get("name", "")
    )
    st.session_state.wizard_data["role"] = st.selectbox(
        "Role", ["Developer", "Designer", "Manager"],
        index=["Developer", "Designer", "Manager"].index(
            st.session_state.wizard_data.get("role", "Developer")
        ),
    )

elif st.session_state.wizard_step == 2:
    st.subheader("Step 2: Preferences")
    st.session_state.wizard_data["notifications"] = st.checkbox(
        "Enable notifications", value=st.session_state.wizard_data.get("notifications", True)
    )
    st.session_state.wizard_data["theme"] = st.radio(
        "Theme", ["Light", "Dark"],
        index=["Light", "Dark"].index(st.session_state.wizard_data.get("theme", "Light")),
        horizontal=True,
    )

elif st.session_state.wizard_step == 3:
    st.subheader("Step 3: Review & Confirm")
    st.json(st.session_state.wizard_data)

nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 2])
with nav_col1:
    st.button("← Back", on_click=prev_step, disabled=st.session_state.wizard_step == 1)
with nav_col2:
    if st.session_state.wizard_step < TOTAL_STEPS:
        st.button("Next →", on_click=next_step)
    else:
        if st.button("Finish ✅"):
            st.success("Wizard completed! Data saved to session state.")
with nav_col3:
    st.button("Restart wizard", on_click=reset_wizard)

st.markdown("---")

# ============================================================================
# SECTION 6: Dynamic input lists (add/remove rows)
# ============================================================================
st.header("6. Dynamic Repeating Inputs (Add/Remove Rows)")

if "items" not in st.session_state:
    st.session_state.items = [{"label": "", "qty": 1}]


def add_item():
    st.session_state.items.append({"label": "", "qty": 1})


def remove_item(index):
    st.session_state.items.pop(index)


for i, item in enumerate(st.session_state.items):
    row_col1, row_col2, row_col3 = st.columns([3, 1, 1])
    with row_col1:
        st.session_state.items[i]["label"] = st.text_input(
            f"Item {i + 1}", value=item["label"], key=f"item_label_{i}"
        )
    with row_col2:
        st.session_state.items[i]["qty"] = st.number_input(
            "Qty", min_value=1, value=item["qty"], key=f"item_qty_{i}"
        )
    with row_col3:
        st.write("")  # vertical spacer
        st.button("Remove", key=f"remove_{i}", on_click=remove_item, args=(i,))

st.button("+ Add item", on_click=add_item)

if any(item["label"] for item in st.session_state.items):
    st.write("Current list:")
    st.dataframe(pd.DataFrame(st.session_state.items), use_container_width=True)

st.markdown("---")

# ============================================================================
# SECTION 7: "Apply" pattern — avoid rerunning on every keystroke
# ============================================================================
st.header("7. Apply Pattern (Deferred / Debounced Updates)")
st.write(
    "Widgets without a form rerun the whole app on every interaction. "
    "Wrapping inputs in a form (or requiring an explicit 'Apply' click) "
    "defers the expensive computation until the user is ready."
)

if "applied_threshold" not in st.session_state:
    st.session_state.applied_threshold = 50

with st.form("apply_form"):
    pending_threshold = st.slider("Threshold (not applied yet)", 0, 100, st.session_state.applied_threshold)
    apply_clicked = st.form_submit_button("Apply")

if apply_clicked:
    st.session_state.applied_threshold = pending_threshold
    st.session_state.log.append(f"Threshold applied -> {pending_threshold}")

st.write(f"Currently applied threshold used by the rest of the app: **{st.session_state.applied_threshold}**")

st.markdown("---")
st.caption("Reference implementation for input handling & session state management in Streamlit.")