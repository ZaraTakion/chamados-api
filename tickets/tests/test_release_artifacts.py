"""CHM-602 — Validate reproducible release artifacts, no embedded secrets."""

import json
from pathlib import Path

from django.test import SimpleTestCase

ROOT = Path(__file__).resolve().parents[2]
COLLECTION = ROOT / "postman" / "Chamados-API-Local-Demo.postman_collection.json"


class ReleaseArtifactsTests(SimpleTestCase):
    def setUp(self):
        self.document = json.loads(COLLECTION.read_text(encoding="utf-8"))
        self.requests = []
        for section in self.document["item"]:
            self.requests.extend(section["item"])

    def test_postman_collection_schema_and_endpoint_coverage(self):
        self.assertEqual(
            self.document["info"]["schema"],
            "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        )
        self.assertEqual(len(self.requests), 18)
        paths = {item["request"]["url"]["raw"] for item in self.requests}
        for path in (
            "/api/health/live/",
            "/api/health/ready/",
            "/api/auth/register/",
            "/api/auth/token/",
            "/api/auth/me/",
            "/api/tickets/",
            "/api/tickets/{{ticketId}}/",
            "/api/notifications/",
        ):
            self.assertIn("{{baseUrl}}" + path, paths)

    def test_default_collection_contains_no_tokens_or_passwords(self):
        data = COLLECTION.read_text(encoding="utf-8")
        variables = {var["key"]: var["value"] for var in self.document["variable"]}
        self.assertEqual(variables["baseUrl"], "http://127.0.0.1:8000")
        for field in (
            "requesterPassword", "staffPassword",
            "requesterAccessToken", "staffAccessToken",
        ):
            self.assertEqual(variables[field], "")
        self.assertNotIn("eyJhbGci", data)
        self.assertNotIn("rdgzrt2121", data)
        self.assertNotIn("SUA_SENHA_FORTE_AQUI", data)
        self.assertIn("PREENCHA_LOCALMENTE", data)

    def test_team_inbox_bearer_and_guest_401(self):
        inbox = [
            i for i in self.requests
            if i["request"]["url"]["raw"] == "{{baseUrl}}/api/notifications/"
        ]
        self.assertEqual(len(inbox), 3)
        staff = next(i for i in inbox if "Inbox equipe" in i["name"])
        guest = next(i for i in inbox if "sem token" in i["name"])
        self.assertEqual(staff["request"]["auth"]["type"], "bearer")
        self.assertEqual(staff["request"]["auth"]["bearer"][0]["value"], "{{staffAccessToken}}")
        self.assertEqual(guest["request"]["auth"]["type"], "noauth")

    def test_portfolio_and_release_notes_declare_local_only(self):
        for name in (
            "docs/ARCHITECTURE.md",
            "docs/PORTFOLIO.md",
            "docs/EVIDENCE.md",
            "docs/POSTMAN.md",
            "docs/RELEASE_NOTES.md",
            "CHANGELOG.md",
        ):
            content = (ROOT / name).read_text(encoding="utf-8")
            self.assertGreater(len(content), 300, name)
        notes = (ROOT / "docs" / "RELEASE_NOTES.md").read_text(encoding="utf-8")
        self.assertIn("v1.0.0-local.1", notes)
        self.assertIn("sem serviço público", notes)
        self.assertIn("não autorizou", notes)
        evidence = (ROOT / "docs" / "EVIDENCE.md").read_text(encoding="utf-8")
        self.assertIn("não", evidence.lower())
        self.assertIn("swagger-ci-capture", evidence)

    def test_release_job_requires_explicit_tag_trigger_and_ci(self):
        workflow = (ROOT / ".github" / "workflows" / "tests.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("swagger-ci-capture", workflow)
        self.assertIn("google-chrome --headless", workflow)
        self.assertIn("github.event.head_commit.message", workflow)
        self.assertIn("release: v1.0.0-local.1", workflow)
        self.assertIn("needs: [quality, postgresql, celery_worker, railway_iac]", workflow)
        self.assertIn("--prerelease", workflow)
