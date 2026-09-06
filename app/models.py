from dataclasses import asdict, dataclass
from enum import StrEnum
from urllib.parse import urlparse, urlunparse


class ApplicationStatus(StrEnum):
    SAVED = "saved"
    REVIEWING = "reviewing"
    READY = "ready"
    APPLIED = "applied"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class Profile:
    first_name: str
    last_name: str
    email: str
    phone: str = ""
    location: str = ""
    summary: str = ""

    def validate(self) -> None:
        if not self.first_name.strip() or not self.last_name.strip():
            raise ValueError("First and last name are required.")
        local, separator, domain = self.email.strip().partition("@")
        if not separator or not local or "." not in domain:
            raise ValueError("Enter a valid email address.")

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class Job:
    url: str
    company: str = ""
    title: str = ""

    def normalized_url(self) -> str:
        parsed = urlparse(self.url.strip())
        host = (parsed.hostname or "").lower()
        if parsed.scheme.lower() not in {"http", "https"}:
            raise ValueError("The job URL must use HTTP or HTTPS.")
        if host not in {"boards.greenhouse.io", "job-boards.greenhouse.io"}:
            raise ValueError("Only Greenhouse job URLs are supported for now.")
        if parsed.username or parsed.password or not parsed.path.strip("/"):
            raise ValueError("Enter a valid Greenhouse job URL.")
        return urlunparse(("https", host, parsed.path.rstrip("/"), "", parsed.query, ""))
