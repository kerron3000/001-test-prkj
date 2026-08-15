from streamlit.testing.v1 import AppTest


APP_PATH = "defect-tracker.py"


def test_app_runs_without_exception():
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=10)
    assert not at.exception


def test_seed_defects_present():
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=10)
    # Title should render
    assert any("Bug Tracker" in t.value for t in at.title)


def test_add_defect_via_sidebar_form():
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=10)

    # Fill the sidebar "Add Defect Report" form
    at.text_input(key=None).first  # placeholder — adjust keys below to match widget order
    # Streamlit AppTest addresses widgets by type + index unless keys are set.
    # Recommend adding explicit `key=` args to widgets in the app for reliable testing, e.g.:
    #   st.text_input("Title*", key="title_input")
    #   st.text_area("Description", key="desc_input")
    #   st.selectbox("Severity", SEVERITIES, key="severity_input")
    #   st.text_input("Reporter", key="reporter_input")
    #   st.form_submit_button("Add Defect", key="add_defect_submit")

    at.text_input(key="title_input").input("New test defect").run()
    at.text_area(key="desc_input").input("Found during automated test").run()
    at.selectbox(key="severity_input").select("High").run()
    at.text_input(key="reporter_input").input("CI Bot").run()
    at.button(key="add_defect_submit").click().run()

    assert not at.exception
    # New defect should appear somewhere in the rendered markdown/captions
    all_text = " ".join(m.value for m in at.markdown) + " ".join(c.value for c in at.caption)
    assert "New test defect" in all_text


def test_metrics_reflect_defect_counts():
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=10)
    metric_labels = [m.label for m in at.metric]
    assert "Total" in metric_labels
    assert "Open" in metric_labels
    assert "In Progress" in metric_labels
    assert "Completed" in metric_labels