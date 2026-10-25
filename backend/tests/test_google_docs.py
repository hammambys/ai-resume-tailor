import unittest
from unittest.mock import patch

import httpx
from flask import Flask

from routes.resume import resume_bp
from services import google_docs


HTTPX_CLIENT = httpx.Client


class GoogleDocsTests(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        app.register_blueprint(resume_bp, url_prefix="/api")
        self.client = app.test_client()

    def test_extracts_document_id_from_standard_link(self):
        document_id = google_docs.extract_google_doc_id(
            "https://docs.google.com/document/d/12345678901234567890/edit?usp=sharing"
        )

        self.assertEqual(document_id, "12345678901234567890")

    def test_rejects_non_google_hosts(self):
        with self.assertRaises(google_docs.GoogleDocsError):
            google_docs.extract_google_doc_id(
                "https://docs.google.com.evil.example/document/d/12345678901234567890/edit"
            )

    def test_rejects_local_urls(self):
        with self.assertRaises(google_docs.GoogleDocsError):
            google_docs.extract_google_doc_id("http://127.0.0.1/document/d/12345678901234567890")

    def test_fetches_text_from_fixed_google_export_url(self):
        requested_urls = []

        def handle_request(request):
            requested_urls.append(str(request.url))
            return httpx.Response(200, headers={"content-type": "text/plain"}, text="Resume content")

        def make_client(*args, **kwargs):
            return HTTPX_CLIENT(transport=httpx.MockTransport(handle_request), *args, **kwargs)

        with patch.object(google_docs.httpx, "Client", side_effect=make_client):
            text = google_docs.fetch_google_doc_text(
                "https://docs.google.com/document/d/12345678901234567890/edit"
            )

        self.assertEqual(text, "Resume content")
        self.assertEqual(
            requested_urls,
            ["https://docs.google.com/document/d/12345678901234567890/export?format=txt"],
        )

    def test_reports_documents_that_require_sign_in(self):
        def handle_request(_request):
            return httpx.Response(302, headers={"location": "https://accounts.google.com/"})

        def make_client(*args, **kwargs):
            return HTTPX_CLIENT(transport=httpx.MockTransport(handle_request), *args, **kwargs)

        with patch.object(google_docs.httpx, "Client", side_effect=make_client):
            with self.assertRaisesRegex(google_docs.GoogleDocsError, "Anyone with the link"):
                google_docs.fetch_google_doc_text(
                    "https://docs.google.com/document/d/12345678901234567890/edit"
                )

    def test_follows_google_export_redirect(self):
        requested_urls = []

        def handle_request(request):
            requested_urls.append(str(request.url))
            if len(requested_urls) == 1:
                return httpx.Response(
                    302,
                    headers={
                        "location": (
                            "https://doc-00-00-sheets.googleusercontent.com/exported"
                        )
                    },
                )
            return httpx.Response(200, headers={"content-type": "text/plain"}, text="Resume content")

        def make_client(*args, **kwargs):
            return HTTPX_CLIENT(transport=httpx.MockTransport(handle_request), *args, **kwargs)

        with patch.object(google_docs.httpx, "Client", side_effect=make_client):
            text = google_docs.fetch_google_doc_text(
                "https://docs.google.com/document/d/12345678901234567890/edit"
            )

        self.assertEqual(text, "Resume content")
        self.assertEqual(len(requested_urls), 2)
        self.assertTrue(requested_urls[1].startswith("https://doc-00-00-sheets.googleusercontent.com/"))

    def test_rejects_redirects_to_untrusted_hosts(self):
        requested_urls = []

        def handle_request(request):
            requested_urls.append(str(request.url))
            return httpx.Response(302, headers={"location": "https://example.com/export"})

        def make_client(*args, **kwargs):
            return HTTPX_CLIENT(transport=httpx.MockTransport(handle_request), *args, **kwargs)

        with patch.object(google_docs.httpx, "Client", side_effect=make_client):
            with self.assertRaisesRegex(google_docs.GoogleDocsError, "unsupported export location"):
                google_docs.fetch_google_doc_text(
                    "https://docs.google.com/document/d/12345678901234567890/edit"
                )

        self.assertEqual(len(requested_urls), 1)

    @patch("routes.resume.tailor_resume", return_value={"name": "Resume"})
    @patch("routes.resume.fetch_google_doc_text", return_value="Resume text")
    def test_tailor_route_accepts_google_doc_link(self, fetch_doc, _tailor_resume):
        response = self.client.post(
            "/api/tailor",
            data={
                "google_doc_url": "https://docs.google.com/document/d/12345678901234567890/edit",
                "job_description": "Developer",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["tailored_resume"], {"name": "Resume"})
        fetch_doc.assert_called_once_with(
            "https://docs.google.com/document/d/12345678901234567890/edit"
        )

    def test_tailor_route_requires_exactly_one_resume_source(self):
        response = self.client.post(
            "/api/tailor",
            data={"job_description": "Developer"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Google Docs link", response.json["error"])


if __name__ == "__main__":
    unittest.main()
