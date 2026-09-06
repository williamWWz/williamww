import sqlite3
from app.models import ApplicationStatus, Job, Profile

class ApplicationService:
    def __init__(self, repository): self.repository = repository
    def save_profile(self, **fields): self.repository.save_profile(Profile(**fields))
    def add_job(self, url, company="", title=""):
        try: return self.repository.add_job(Job(url=url, company=company, title=title))
        except sqlite3.IntegrityError as error: raise ValueError("This job is already saved.") from error
    def move_application(self, application_id, status, notes=""):
        try: parsed = ApplicationStatus(status)
        except ValueError as error: raise ValueError("Unknown application status.") from error
        self.repository.update_application(application_id, parsed, notes)
