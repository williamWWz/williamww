import streamlit as st
import json
import os
import time
from app.utils.profile_manager import load_profile, save_profile, get_default_profile
from app.services.job_queue import JobQueue, JobSearcher
from app.services.automator import GreenhouseAutomator

st.set_page_config(page_title="Auto-Apply Bot", page_icon="🤖", layout="wide")

st.title("🤖 Intelligent Job Auto-Submitter")
st.markdown("Automatically apply to Greenhouse jobs using your profile and an AI Assistant to answer custom questions.")

# Initialize Session State
if 'profile' not in st.session_state:
    st.session_state.profile = load_profile() or get_default_profile()
if 'job_queue' not in st.session_state:
    st.session_state.job_queue = JobQueue()
if 'resume_path' not in st.session_state:
    st.session_state.resume_path = "app/data/resume.pdf" # default placeholder

# Tabs
tab_profile, tab_jobs, tab_logs = st.tabs(["Profile & Resume", "Job Search & Queue", "Application Logs"])

with tab_profile:
    st.header("Your Profile Config")
    st.markdown("Edit your profile below. The LLM will use this to answer questions in English or Chinese.")

    # Simple JSON editor for now
    profile_str = json.dumps(st.session_state.profile, indent=4, ensure_ascii=False)
    new_profile_str = st.text_area("Profile JSON", value=profile_str, height=400)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save Profile"):
            try:
                st.session_state.profile = json.loads(new_profile_str)
                save_profile(st.session_state.profile)
                st.success("Profile saved successfully!")
            except json.JSONDecodeError:
                st.error("Invalid JSON format. Please check your syntax.")

    with col2:
        uploaded_resume = st.file_uploader("Upload Resume (PDF/DOCX)", type=['pdf', 'docx'])
        if uploaded_resume is not None:
            save_path = os.path.join("app/data", uploaded_resume.name)
            with open(save_path, "wb") as f:
                f.write(uploaded_resume.getbuffer())
            st.session_state.resume_path = save_path
            st.success(f"Saved resume to {save_path}")

with tab_jobs:
    st.header("Add Jobs to Queue")

    col_direct, col_search = st.columns(2)

    with col_direct:
        st.subheader("Direct URLs")
        st.markdown("Paste Greenhouse job URLs (one per line):")
        urls_input = st.text_area("URLs", height=150)
        if st.button("Add URLs to Queue"):
            st.session_state.job_queue.add_urls(urls_input)
            st.success(f"Added URLs. Total in queue: {len(st.session_state.job_queue.queue)}")

    with col_search:
        st.subheader("Search & Apply")
        st.markdown("Search for Greenhouse jobs using keywords:")
        search_keywords = st.text_input("Keywords (e.g., Software Engineer Remote)")
        num_results = st.number_input("Max results to fetch", min_value=1, max_value=20, value=5)

        if st.button("Search & Add to Queue"):
            with st.spinner("Searching..."):
                searcher = JobSearcher()
                found_urls = searcher.search_greenhouse_jobs(search_keywords, num_results=num_results)
                for url in found_urls:
                    st.session_state.job_queue.queue.append(url)
                st.success(f"Found and added {len(found_urls)} jobs. Total in queue: {len(st.session_state.job_queue.queue)}")

    st.divider()
    st.subheader("Current Queue")
    st.write(st.session_state.job_queue.queue)

    if st.button("Start Applying!", type="primary"):
        if not st.session_state.job_queue.queue:
            st.warning("Queue is empty!")
        elif not os.environ.get("OPENAI_API_KEY_CHAT") and not os.environ.get("OPENAI_API_KEY"):
            st.error("Please set the OPENAI_API_KEY_CHAT or OPENAI_API_KEY environment variable for the LLM Assistant.")
        else:
            st.info("Starting automation... (Submit button is disabled by default for safety)")
            automator = GreenhouseAutomator(st.session_state.profile, st.session_state.resume_path)

            # Process queue
            # We'll just do one iteration for the PoC, or loop with a status bar
            queue_length = len(st.session_state.job_queue.queue)
            progress_bar = st.progress(0)
            status_text = st.empty()

            for i in range(queue_length):
                job_url = st.session_state.job_queue.get_next_job()
                status_text.text(f"Processing ({i+1}/{queue_length}): {job_url}")

                success, msg = automator.run_application(job_url)

                st.session_state.job_queue.add_result(job_url, "Success" if success else "Failed", msg)
                progress_bar.progress((i + 1) / queue_length)

            status_text.text("Finished processing queue!")
            st.success("Done! Check Application Logs tab.")

            if os.path.exists("app/data/last_application.png"):
                st.image("app/data/last_application.png", caption="Last Filled Application Screenshot")

with tab_logs:
    st.header("Application Results")
    if not st.session_state.job_queue.results:
        st.write("No applications processed yet.")
    else:
        for res in reversed(st.session_state.job_queue.results):
            if res["status"] == "Success":
                st.success(f"**{res['time']}** - {res['url']}\n\n{res['message']}")
            else:
                st.error(f"**{res['time']}** - {res['url']}\n\n{res['message']}")
