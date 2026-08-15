import streamlit as st
import pandas as pd
import uuid
from datetime import datetime

# --------------------------------------------------------------------------
# Page config
# --------------------------------------------------------------------------
st.set_page_config(page_title="Bug Tracker", page_icon="🐞", layout="wide")

STATUSES = ["Open", "In Progress", "Completed"]
SEVERITIES = ["Low", "Medium", "High", "Critical"]

SEVERITY_COLORS = {
    "Low": "#4CAF50",
    "Medium": "#FFC107",
    "High": "#FF9800",
    "Critical": "#F44336",
}

STATUS_COLORS = {
    "Open": "#e3f2fd",
    "In Progress": "#fff8e1",
    "Completed": "#e8f5e9",
}

# --------------------------------------------------------------------------
# Session state initialization
# --------------------------------------------------------------------------
if "defects" not in st.session_state:
    # seed with a couple of sample defects so the board isn't empty
    st.session_state.defects = {}

    def _seed(title, description, severity, status, reporter):
        did = str(uuid.uuid4())[:8]
        st.session_state.defects[did] = {
            "id": did,
            "title": title,
            "description": description,
            "severity": severity,
            "status": status,
            "reporter": reporter,
            "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

    _seed("Login button unresponsive on Safari", "Clicking 'Login' does nothing on Safari 17.", "High", "Open", "A. Smith")
    _seed("Typo in footer copyright year", "Footer shows 2023 instead of current year.", "Low", "Open", "J. Lee")
    _seed("Checkout fails for international cards", "Payment gateway times out for non-US cards.", "Critical", "In Progress", "M. Chen")
    _seed("Dark mode toggle resets on refresh", "User preference not persisted after page reload.", "Medium", "Completed", "A. Smith")

if "editing_id" not in st.session_state:
    st.session_state.editing_id = None


# --------------------------------------------------------------------------
# Helper functions
# --------------------------------------------------------------------------
def add_defect(title, description, severity, reporter, status="Open"):
    did = str(uuid.uuid4())[:8]
    st.session_state.defects[did] = {
        "id": did,
        "title": title,
        "description": description,
        "severity": severity,
        "status": status,
        "reporter": reporter,
        "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


def update_defect(did, **fields):
    if did in st.session_state.defects:
        st.session_state.defects[did].update(fields)
        st.session_state.defects[did]["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")


def delete_defect(did):
    st.session_state.defects.pop(did, None)


def transition(did, new_status):
    update_defect(did, status=new_status)


def next_status(current):
    idx = STATUSES.index(current)
    return STATUSES[idx + 1] if idx + 1 < len(STATUSES) else None


def prev_status(current):
    idx = STATUSES.index(current)
    return STATUSES[idx - 1] if idx - 1 >= 0 else None


# --------------------------------------------------------------------------
# Sidebar: Add new defect
# --------------------------------------------------------------------------
with st.sidebar:
    st.header("➕ Add Defect Report")
    with st.form("add_defect_form", clear_on_submit=True):
        title = st.text_input("Title*", placeholder="Short summary of the defect")
        description = st.text_area("Description", placeholder="Steps to reproduce, expected vs actual behavior...")
        severity = st.selectbox("Severity", SEVERITIES, index=1)
        reporter = st.text_input("Reporter", placeholder="Your name")
        status = st.selectbox("Initial Status", STATUSES, index=0)
        submitted = st.form_submit_button("Add Defect", use_container_width=True)

        if submitted:
            if not title.strip():
                st.error("Title is required.")
            else:
                add_defect(title.strip(), description.strip(), severity, reporter.strip() or "Unassigned", status)
                st.success(f"Defect '{title}' added.")
                st.rerun()

    st.divider()
    st.caption(f"Total defects: {len(st.session_state.defects)}")
    if st.button("🗑️ Clear All Defects", use_container_width=True):
        st.session_state.defects = {}
        st.rerun()


# --------------------------------------------------------------------------
# Header
# --------------------------------------------------------------------------
st.title("🐞 Bug Tracker")
st.caption("Kanban-style defect tracking — Open → In Progress → Completed")

# Quick metrics
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
all_defects = list(st.session_state.defects.values())
col_m1.metric("Total", len(all_defects))
col_m2.metric("Open", sum(1 for d in all_defects if d["status"] == "Open"))
col_m3.metric("In Progress", sum(1 for d in all_defects if d["status"] == "In Progress"))
col_m4.metric("Completed", sum(1 for d in all_defects if d["status"] == "Completed"))

st.divider()


# --------------------------------------------------------------------------
# Edit modal (rendered via dialog if available, else inline expander)
# --------------------------------------------------------------------------
def render_edit_form(did):
    defect = st.session_state.defects[did]
    st.subheader(f"Edit Defect — {defect['id']}")
    with st.form(f"edit_form_{did}"):
        title = st.text_input("Title*", value=defect["title"])
        description = st.text_area("Description", value=defect["description"])
        severity = st.selectbox("Severity", SEVERITIES, index=SEVERITIES.index(defect["severity"]))
        reporter = st.text_input("Reporter", value=defect["reporter"])
        status = st.selectbox("Status", STATUSES, index=STATUSES.index(defect["status"]))

        col_a, col_b = st.columns(2)
        save = col_a.form_submit_button("💾 Save Changes", use_container_width=True)
        cancel = col_b.form_submit_button("Cancel", use_container_width=True)

        if save:
            if not title.strip():
                st.error("Title is required.")
            else:
                update_defect(
                    did,
                    title=title.strip(),
                    description=description.strip(),
                    severity=severity,
                    reporter=reporter.strip() or "Unassigned",
                    status=status,
                )
                st.session_state.editing_id = None
                st.rerun()
        if cancel:
            st.session_state.editing_id = None
            st.rerun()


# Use st.dialog if the installed Streamlit version supports it, else fall back
_has_dialog = hasattr(st, "dialog")

if st.session_state.editing_id and _has_dialog:
    @st.dialog("Edit Defect Report")
    def _edit_dialog():
        render_edit_form(st.session_state.editing_id)

    _edit_dialog()
elif st.session_state.editing_id and not _has_dialog:
    with st.expander("✏️ Edit Defect Report", expanded=True):
        render_edit_form(st.session_state.editing_id)


# --------------------------------------------------------------------------
# Kanban board
# --------------------------------------------------------------------------
def render_card(defect):
    did = defect["id"]
    sev_color = SEVERITY_COLORS.get(defect["severity"], "#999")

    with st.container(border=True):
        st.markdown(
            f"""
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:600; font-size:1rem;">{defect['title']}</span>
                <span style="background:{sev_color}; color:white; padding:2px 8px;
                             border-radius:10px; font-size:0.75rem; white-space:nowrap;">
                    {defect['severity']}
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if defect["description"]:
            desc = defect["description"]
            preview = (desc[:90] + "…") if len(desc) > 90 else desc
            st.caption(preview)

        st.markdown(
            f"<span style='font-size:0.75rem; color:gray;'>#{did} · 👤 {defect['reporter']} · updated {defect['updated']}</span>",
            unsafe_allow_html=True,
        )

        st.write("")  # spacing
        b1, b2, b3, b4 = st.columns([1, 1, 1, 1])

        prev_s = prev_status(defect["status"])
        next_s = next_status(defect["status"])

        if prev_s and b1.button("⬅️", key=f"prev_{did}", help=f"Move back to {prev_s}", use_container_width=True):
            transition(did, prev_s)
            st.rerun()

        if next_s and b2.button("➡️", key=f"next_{did}", help=f"Move to {next_s}", use_container_width=True):
            transition(did, next_s)
            st.rerun()

        if b3.button("✏️", key=f"edit_{did}", help="Edit defect", use_container_width=True):
            st.session_state.editing_id = did
            st.rerun()

        if b4.button("🗑️", key=f"del_{did}", help="Delete defect", use_container_width=True):
            delete_defect(did)
            st.rerun()


cols = st.columns(3)

for col, status in zip(cols, STATUSES):
    with col:
        status_defects = [d for d in st.session_state.defects.values() if d["status"] == status]
        st.markdown(
            f"""
            <div style="background:{STATUS_COLORS[status]}; padding:10px; border-radius:8px; margin-bottom:10px;">
                <h4 style="margin:0;">{status} ({len(status_defects)})</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not status_defects:
            st.info("No defects here.")
        else:
            # Sort by severity (Critical first) then by updated time
            severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
            status_defects.sort(key=lambda d: (severity_order.get(d["severity"], 4), d["updated"]), reverse=False)
            for defect in status_defects:
                render_card(defect)

st.divider()

# --------------------------------------------------------------------------
# Optional: table view / export
# --------------------------------------------------------------------------
with st.expander("📋 View All Defects as Table"):
    if st.session_state.defects:
        df = pd.DataFrame(st.session_state.defects.values())
        df = df[["id", "title", "severity", "status", "reporter", "created", "updated", "description"]]
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button(
            "⬇️ Download as CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="defect_report.csv",
            mime="text/csv",
        )
    else:
        st.write("No defects to display.")