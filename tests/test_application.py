import tempfile
import unittest
from pathlib import Path

from app.models import ApplicationStatus
from app.repository import Repository
from app.service import ApplicationService

class ApplicationServiceTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.repository = Repository(Path(self.tempdir.name) / "test.db")
        self.service = ApplicationService(self.repository)
    def tearDown(self): self.tempdir.cleanup()
    def test_profile_round_trip(self):
        self.service.save_profile(first_name="Ada", last_name="Lovelace", email="ada@example.com", phone="", location="London", summary="Engineer")
        self.assertEqual(self.repository.load_profile().email, "ada@example.com")
    def test_profile_rejects_invalid_email(self):
        with self.assertRaisesRegex(ValueError, "valid email"):
            self.service.save_profile(first_name="Ada", last_name="Lovelace", email="invalid", phone="", location="", summary="")
    def test_job_lifecycle_is_persistent(self):
        job_id = self.service.add_job("https://boards.greenhouse.io/acme/jobs/123", "Acme", "Engineer")
        self.service.move_application(job_id, ApplicationStatus.READY.value, "Reviewed")
        item = self.repository.list_applications()[0]
        self.assertEqual((item["status"], item["notes"]), ("ready", "Reviewed"))
    def test_rejects_duplicate_and_deceptive_urls(self):
        url = "https://boards.greenhouse.io/acme/jobs/123"
        self.service.add_job(url)
        with self.assertRaisesRegex(ValueError, "already saved"): self.service.add_job(url)
        with self.assertRaisesRegex(ValueError, "Only Greenhouse"):
            self.service.add_job("https://boards.greenhouse.io.example.com/jobs/123")

if __name__ == "__main__": unittest.main()
