import re
from urllib.parse import urljoin, urlsplit

import httpx


MAX_DOCUMENT_BYTES = 2 * 1024 * 1024
MAX_REDIRECTS = 5
DOCUMENT_PATH_PATTERN = re.compile(r"^/document/(?:u/\d+/)?d/([A-Za-z0-9_-]{10,200})(?:/|$)")


class GoogleDocsError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


def extract_google_doc_id(document_url: str) -> str:
    try:
        parsed_url = urlsplit(document_url.strip())
        port = parsed_url.port
    except ValueError as exc:
        raise GoogleDocsError("Enter a valid Google Docs link.") from exc

    if (
        parsed_url.scheme != "https"
        or parsed_url.hostname != "docs.google.com"
        or port not in (None, 443)
        or parsed_url.username
        or parsed_url.password
    ):
        raise GoogleDocsError("Enter a link from https://docs.google.com.")

    match = DOCUMENT_PATH_PATTERN.match(parsed_url.path)
    if not match:
        raise GoogleDocsError("Enter a link to a Google Docs document.")

    return match.group(1)


def _is_allowed_google_redirect(url: str) -> bool:
    try:
        parsed_url = urlsplit(url)
        port = parsed_url.port
    except ValueError:
        return False

    hostname = parsed_url.hostname or ""
    return (
        parsed_url.scheme == "https"
        and port in (None, 443)
        and not parsed_url.username
        and not parsed_url.password
        and (
            hostname == "docs.google.com"
            or hostname.endswith(".googleusercontent.com")
        )
    )


def fetch_google_doc_text(document_url: str) -> str:
    document_id = extract_google_doc_id(document_url)
    current_url = f"https://docs.google.com/document/d/{document_id}/export?format=txt"

    try:
        with httpx.Client(timeout=15.0, follow_redirects=False) as client:
            for redirect_count in range(MAX_REDIRECTS + 1):
                with client.stream("GET", current_url) as response:
                    if response.status_code in (301, 302, 303, 307, 308):
                        location = response.headers.get("location")
                        if not location:
                            raise GoogleDocsError(
                                "Google Docs returned an invalid export redirect.",
                                502,
                            )
                        if redirect_count == MAX_REDIRECTS:
                            raise GoogleDocsError(
                                "Google Docs returned too many export redirects.",
                                502,
                            )

                        redirect_url = urljoin(current_url, location)
                        redirect_host = urlsplit(redirect_url).hostname
                        if redirect_host == "accounts.google.com":
                            raise GoogleDocsError(
                                "This document is not publicly accessible. Set General access to "
                                '"Anyone with the link" and try again.'
                            )
                        if not _is_allowed_google_redirect(redirect_url):
                            raise GoogleDocsError(
                                "Google Docs redirected to an unsupported export location.",
                                502,
                            )
                        current_url = redirect_url
                        continue

                    if response.status_code in (401, 403, 404):
                        raise GoogleDocsError(
                            "This document could not be accessed. Set General access to "
                            '"Anyone with the link" and try again.'
                        )
                    if response.status_code != 200:
                        raise GoogleDocsError(
                            "Google Docs could not export this document. Please try again later.",
                            502,
                        )

                    content_type = response.headers.get("content-type", "").lower()
                    if "text/html" in content_type:
                        raise GoogleDocsError(
                            "This document is not publicly accessible. Set General access to "
                            '"Anyone with the link" and try again.'
                        )

                    content_length = response.headers.get("content-length")
                    if content_length:
                        try:
                            if int(content_length) > MAX_DOCUMENT_BYTES:
                                raise GoogleDocsError("The Google Doc is too large to import.")
                        except ValueError:
                            pass

                    content = bytearray()
                    for chunk in response.iter_bytes():
                        content.extend(chunk)
                        if len(content) > MAX_DOCUMENT_BYTES:
                            raise GoogleDocsError("The Google Doc is too large to import.")
                    break
            else:
                raise GoogleDocsError(
                    "Google Docs returned too many export redirects.",
                    502,
                )
    except httpx.TimeoutException as exc:
        raise GoogleDocsError(
            "Timed out while retrieving the Google Doc. Please try again.",
            502,
        ) from exc
    except httpx.HTTPError as exc:
        raise GoogleDocsError(
            "Could not retrieve the Google Doc. Please try again later.",
            502,
        ) from exc

    text = content.decode("utf-8-sig", errors="replace").strip()
    if not text or text.lstrip().startswith("<"):
        raise GoogleDocsError(
            "No document text was found. Check that the link is publicly accessible."
        )

    return text
