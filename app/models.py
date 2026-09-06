from dataclasses import dataclass
from enum import StrEnum
from urllib.parse import urlparse

class ApplicationStatus(StrEnum):
    SAVED = "saved"
    REVIEWING = "reviewing"
    READY = "ready"
    APPLIED = "applied"
    REJECTED = "rejected"

@dataclass(frozen=True)
class Profile:
    first_name: str
    last_name: str
    email: str
    phone: str = ""
    location: str = ""
    summary: str = ""
    def validate(self):
        if not self.first_name.strip() or not self.last_name.strip(): raise ValueError("First and last name are required.")
        if "@" not in self.email or self.email.startswith("@"): raise ValueError("Enter a valid email address.")

@dataclass(frozen=True)
class Job:
    url: str
    company: str = ""
    title: str = ""
    def validate(self):
        parsed = urlparse(self.url.strip()); host = (parsed.hostname or "").lower()
        if parsed.scheme not in {"http", "https"}: raise ValueError("The job URL must use HTTP or HTTPS.")
        if host not in {"boards.greenhouse.io", "job-boards.greenhouse.io"}: raise ValueError("Only Greenhouse job URLs are supported for now.")
