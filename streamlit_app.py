import os
import streamlit as st
from app.models import ApplicationStatus
from app.repository import Repository
from app.service import ApplicationService

st.set_page_config(page_title="Application Desk", page_icon="🗂️", layout="wide")
@st.cache_resource
def get_service(): return ApplicationService(Repository(os.environ.get("APPLICATION_DB", "app/data/applications.db")))
service = get_service()
st.title("🗂️ Application Desk")
st.caption("A private workspace to prepare and review applications. Nothing is submitted automatically.")
profile_tab, jobs_tab, review_tab, history_tab = st.tabs(["👤 Profile", "➕ Add job", "✅ Review", "📚 History"])
with profile_tab:
    profile = service.repository.load_profile()
    with st.form("profile"):
        first, last = st.columns(2)
        first_name = first.text_input("First name", value=profile.first_name if profile else "")
        last_name = last.text_input("Last name", value=profile.last_name if profile else "")
        email = st.text_input("Email", value=profile.email if profile else "")
        phone = st.text_input("Phone", value=profile.phone if profile else "")
        location = st.text_input("Location", value=profile.location if profile else "")
        summary = st.text_area("Professional summary", value=profile.summary if profile else "")
        if st.form_submit_button("Save profile", type="primary"):
            try:
                service.save_profile(first_name=first_name, last_name=last_name, email=email, phone=phone, location=location, summary=summary); st.success("Profile saved locally.")
            except ValueError as error: st.error(str(error))
with jobs_tab:
    st.subheader("Save a Greenhouse role")
    with st.form("job"):
        url = st.text_input("Job URL", placeholder="https://boards.greenhouse.io/…")
        company = st.text_input("Company (optional)"); title = st.text_input("Role title (optional)")
        if st.form_submit_button("Add to review queue", type="primary"):
            try: service.add_job(url, company, title); st.success("Job added to your review queue.")
            except ValueError as error: st.error(str(error))
applications = service.repository.list_applications()
with review_tab:
    pending = [item for item in applications if item["status"] in {"saved", "reviewing", "ready"}]
    if not pending: st.info("Your review queue is empty.")
    for item in pending:
        with st.expander(f'{item["title"] or "Untitled role"} · {item["company"] or "Unknown company"}'):
            st.link_button("Open job posting", item["url"])
            statuses = [status.value for status in ApplicationStatus]
            status = st.selectbox("Status", statuses, index=statuses.index(item["status"]), key=f'status-{item["id"]}')
            notes = st.text_area("Review notes", item["notes"], key=f'notes-{item["id"]}')
            if st.button("Save review", key=f'save-{item["id"]}'):
                service.move_application(item["id"], status, notes); st.rerun()
with history_tab:
    if applications: st.dataframe(applications, hide_index=True, use_container_width=True)
    else: st.info("No applications saved yet.")
