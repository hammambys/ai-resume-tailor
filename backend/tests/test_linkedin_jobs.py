import unittest
from unittest.mock import patch

import httpx
from flask import Flask

from routes.resume import resume_bp
from services import linkedin_jobs


HTTPX_CLIENT = httpx.Client


class LinkedInJobsTests(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        app.register_blueprint(resume_bp, url_prefix="/api")
        self.client = app.test_client()

    def test_rejects_non_linkedin_hosts(self):
        with self.assertRaises(linkedin_jobs.LinkedInJobError):
            linkedin_jobs.fetch_linkedin_job_description(
                "https://www.linkedin.com.evil.example/jobs/view/123456789/"
            )

    def test_rejects_links_that_are_not_specific_job_postings(self):
        with self.assertRaisesRegex(
            linkedin_jobs.LinkedInJobError, "specific job posting"
        ):
            linkedin_jobs.fetch_linkedin_job_description(
                "https://www.linkedin.com/jobs/search/?keywords=developer"
            )

    def test_extracts_job_posting_description_from_json_ld(self):
        html = """
        <html><script type="application/ld+json">
        {"@type":"JobPosting","description":"<p>Build reliable software.</p><ul><li>Use Python</li></ul>"}
        </script></html>
        """

        description = linkedin_jobs._extract_job_description(html)

        self.assertEqual(description, "Build reliable software.\nUse Python")

    def test_extracts_description_from_linkedin_page_content(self):
        html = """
        <div class="show-more-less-html__markup">
          <p>Build reliable software.</p>
          <ul><li>Use Python</li></ul>
        </div>
        """

        description = linkedin_jobs._extract_job_description(html)

        self.assertEqual(description, "Build reliable software.\nUse Python")

    def test_ignores_valueless_html_attributes(self):
        html = """
        <div class>
          <div class="show-more-less-html__markup">
            <p>Build reliable software.</p>
          </div>
        </div>
        """

        description = linkedin_jobs._extract_job_description(html)

        self.assertEqual(description, "Build reliable software.")

    def test_fetches_canonical_public_job_page(self):
        requested_urls = []
        page = """
        <script type="application/ld+json">
        {"@type":"JobPosting","description":"<p>Software Engineer</p>"}
        </script>
        """

        def handle_request(request):
            requested_urls.append(str(request.url))
            return httpx.Response(
                200,
                headers={"content-type": "text/html"},
                text=page,
            )

        def make_client(*args, **kwargs):
            return HTTPX_CLIENT(
                transport=httpx.MockTransport(handle_request),
                *args,
                **kwargs,
            )

        with patch.object(linkedin_jobs.httpx, "Client", side_effect=make_client):
            description = linkedin_jobs.fetch_linkedin_job_description(
                "https://www.linkedin.com/jobs/view/123456789/?trackingId=ignored"
            )

        self.assertEqual(description, "Software Engineer")
        self.assertEqual(
            requested_urls,
            ["https://www.linkedin.com/jobs/view/123456789/"],
        )

    def test_does_not_follow_redirects(self):
        requested_urls = []

        def handle_request(request):
            requested_urls.append(str(request.url))
            return httpx.Response(
                302,
                headers={"location": "https://example.com/internal"},
            )

        def make_client(*args, **kwargs):
            return HTTPX_CLIENT(
                transport=httpx.MockTransport(handle_request),
                *args,
                **kwargs,
            )

        with patch.object(linkedin_jobs.httpx, "Client", side_effect=make_client):
            with self.assertRaises(linkedin_jobs.LinkedInJobError):
                linkedin_jobs.fetch_linkedin_job_description(
                    "https://www.linkedin.com/jobs/view/123456789/"
                )

        self.assertEqual(len(requested_urls), 1)

    @patch(
        "routes.resume.fetch_linkedin_job_description",
        return_value="Build reliable software.",
    )
    def test_extract_route_returns_job_description(self, fetch_job):
        response = self.client.post(
            "/api/extract-job-description",
            json={"url": "https://www.linkedin.com/jobs/view/123456789/"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json["job_description"],
            "Build reliable software.",
        )
        fetch_job.assert_called_once_with(
            "https://www.linkedin.com/jobs/view/123456789/"
        )

    def test_extract_route_requires_link(self):
        response = self.client.post("/api/extract-job-description", json={})

        self.assertEqual(response.status_code, 400)
        self.assertIn("required", response.json["error"])

    def test_extract_route_rejects_invalid_json(self):
        response = self.client.post(
            "/api/extract-job-description",
            data="{",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("valid JSON", response.json["error"])


if __name__ == "__main__":
    unittest.main()
