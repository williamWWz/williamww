import os
import time
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
from bs4 import BeautifulSoup
from app.services.llm_assistant import LLMAssistant

class GreenhouseAutomator:
    def __init__(self, profile_data, resume_path=None):
        self.profile = profile_data
        self.resume_path = resume_path
        self.llm_assistant = LLMAssistant()

    def run_application(self, job_url):
        """
        Runs the full application process for a Greenhouse job URL.
        Returns (success_boolean, status_message)
        """
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False) # Headless=False for debugging/captchas if any
                context = browser.new_context()
                page = context.new_page()

                # Apply stealth to avoid basic bot detection
                stealth_sync(page)

                page.goto(job_url)

                # Wait for the application form to load (Greenhouse usually has #application_form)
                try:
                    page.wait_for_selector('#application_form', timeout=10000)
                except Exception as e:
                    return False, f"Could not find application form on this page. Error: {str(e)}"

                # Extract job description for the LLM
                job_description = ""
                try:
                    content_html = page.content()
                    soup = BeautifulSoup(content_html, 'lxml')
                    desc_div = soup.find('div', id='content')
                    if desc_div:
                        job_description = desc_div.get_text(separator='\n').strip()
                except Exception as e:
                    print(f"Warning: Could not extract job description: {e}")

                # Basic Fields
                personal = self.profile.get("personal_info", {})

                # Fill First Name
                if personal.get("first_name"):
                    page.fill('input[name="job_application[first_name]"]', personal["first_name"])

                # Fill Last Name
                if personal.get("last_name"):
                    page.fill('input[name="job_application[last_name]"]', personal["last_name"])

                # Fill Email
                if personal.get("email"):
                    page.fill('input[name="job_application[email]"]', personal["email"])

                # Fill Phone
                if personal.get("phone"):
                    page.fill('input[name="job_application[phone]"]', personal["phone"])

                # Upload Resume (Greenhouse uses an input type="file" but it might be hidden, usually there's a button, but input works)
                if self.resume_path and os.path.exists(self.resume_path):
                    try:
                        # Find the file input for resume
                        # Depending on the greenhouse setup it could be different
                        # Common: data-source="attach" input type="file"
                        resume_inputs = page.locator('input[type="file"]')
                        if resume_inputs.count() > 0:
                            # Typically the first file input is the resume, but we should be careful.
                            # Greenhouse uses a specific container for resume
                            resume_input = page.locator('button[data-source="attach"]').locator('..').locator('input[type="file"]')
                            if resume_input.count() > 0:
                                resume_input.first.set_input_files(self.resume_path)
                            else:
                                # Fallback, just pick the first file input
                                resume_inputs.first.set_input_files(self.resume_path)

                            # Wait a bit for upload to process (Greenhouse does some parsing sometimes)
                            time.sleep(3)
                    except Exception as e:
                        print(f"Warning: Failed to upload resume: {e}")

                # Custom Questions
                # Custom questions in Greenhouse usually have 'custom_fields' in their name attribute
                custom_questions = page.locator('div.custom_field')
                for i in range(custom_questions.count()):
                    question_div = custom_questions.nth(i)
                    try:
                        # The question text is usually in a label
                        label = question_div.locator('label').first.inner_text().strip()

                        # Strip out the "*" if it's required
                        if label.endswith('*'):
                            label = label[:-1].strip()

                        # Find the input/textarea
                        # It could be input type="text", textarea, or select
                        inputs = question_div.locator('input[type="text"], textarea')
                        if inputs.count() > 0:
                            # Get the answer from LLM
                            answer = self.llm_assistant.answer_question(label, self.profile, job_description)
                            inputs.first.fill(answer)

                        # If it's a dropdown (select), it's harder for the LLM.
                        # A robust PoC might skip dropdowns or ask LLM to pick one.
                        # For now, we leave dropdowns for the user or manual review unless required.
                    except Exception as e:
                        print(f"Warning: Failed to process custom field: {e}")

                # Optional: We will NOT actually click submit during testing to avoid spamming companies!
                # We can return success indicating the form was filled successfully.
                # To actually submit: page.click('#submit_app')

                # Taking a screenshot to prove we filled it out
                page.screenshot(path="app/data/last_application.png")

                browser.close()
                return True, "Form filled successfully! (Submit click is disabled for safety during dev)"

        except Exception as e:
            return False, f"Automation error: {str(e)}"
