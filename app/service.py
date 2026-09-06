import sqlite3

from app.models import ApplicationStatus, Job, Profile
from app.repository import Repository


class ApplicationService:
    def __init__(self, repository: Repository) -> None:
        self.repository = repository

    def save_profile(self, **fields: str) -> None:
        self.repository.save_profile(Profile(**fields))

    def add_job(self, url: str, company: str = "", title: str = "") -> int:
        try:
            return self.repository.add_job(Job(url=url, company=company, title=title))
        except sqlite3.IntegrityError as error:
            raise ValueError("This job is already saved.") from error

    def move_application(
        self, application_id: int, status: str, notes: str = ""
    ) -> None:
        try:
            parsed_status = ApplicationStatus(status)
        except ValueError as error:
            raise ValueError("Unknown application status.") from error
        self.repository.update_application(application_id, parsed_status, notes)

    def delete_application(self, application_id: int) -> None:
        self.repository.delete_application(application_id)
