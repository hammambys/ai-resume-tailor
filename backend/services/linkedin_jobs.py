import json
import re
from html.parser import HTMLParser
from urllib.parse import urlsplit

import httpx


MAX_JOB_PAGE_BYTES = 2 * 1024 * 1024
MAX_JOB_DESCRIPTION_LENGTH = 10_000
JOB_PATH_PATTERN = re.compile(r"^/jobs/view/(\d+)/?$")
DESCRIPTION_CLASSES = {
    "description__text",
    "jobs-description__content",
    "jobs-box__html-content",
    "show-more-less-html__markup",
}
BLOCK_TAGS = {
    "br", "dd", "div", "dl", "dt", "h1", "h2", "h3", "h4", "li",
    "ol", "p", "section", "ul",
}
VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
}


class LinkedInJobError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


class _JobPageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.json_ld_scripts = []
        self._script_parts = None
        self._target_depth = None
        self._depth = 0
        self._description_parts = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if (
            tag == "script"
            and (attributes.get("type") or "").lower() == "application/ld+json"
        ):
            self._script_parts = []

        classes = set((attributes.get("class") or "").split())
        if (
            self._target_depth is None
            and tag in {"div", "section"}
            and classes.intersection(DESCRIPTION_CLASSES)
        ):
            self._target_depth = self._depth

        if self._target_depth is not None and tag in BLOCK_TAGS:
            self._description_parts.append("\n")
        if tag not in VOID_TAGS:
            self._depth += 1

    def handle_endtag(self, tag):
        if self._target_depth is not None and tag in BLOCK_TAGS:
            self._description_parts.append("\n")
        if tag not in VOID_TAGS:
            self._depth = max(0, self._depth - 1)

        if self._target_depth == self._depth:
            self._target_depth = None

        if tag == "script" and self._script_parts is not None:
            self.json_ld_scripts.append("".join(self._script_parts))
            self._script_parts = None

    def handle_data(self, data):
        if self._script_parts is not None:
            self._script_parts.append(data)
        if self._target_depth is not None:
            self._description_parts.append(data)


class _HTMLTextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if (
            tag in BLOCK_TAGS
            and not attributes.get("hidden")
            and attributes.get("aria-hidden") != "true"
        ):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data):
        self.parts.append(data)


def _normalize_text(text: str) -> str:
    text = re.sub(r"[ \t\f\v]+", " ", text)
    lines = [line.strip() for line in text.splitlines()]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(line for line in lines if line)).strip()


def _html_to_text(markup: str) -> str:
    parser = _HTMLTextParser()
    parser.feed(markup)
    return _normalize_text("".join(parser.parts))


def _find_job_description(value):
    if isinstance(value, list):
        for item in value:
            description = _find_job_description(item)
            if description:
                return description
    elif isinstance(value, dict):
        job_type = value.get("@type")
        if (
            job_type == "JobPosting"
            or isinstance(job_type, list) and "JobPosting" in job_type
        ):
            description = value.get("description")
            if isinstance(description, str) and description.strip():
                return description

        for item in value.values():
            description = _find_job_description(item)
            if description:
                return description
    return None


def _extract_job_description(html: str) -> str:
    parser = _JobPageParser()
    parser.feed(html)

    for script in parser.json_ld_scripts:
        try:
            data = json.loads(script)
        except json.JSONDecodeError:
            continue
        description = _find_job_description(data)
        if description:
            text = _html_to_text(description)
            if text:
                return text[:MAX_JOB_DESCRIPTION_LENGTH]

    description = _normalize_text("".join(parser._description_parts))
    if description:
        return description[:MAX_JOB_DESCRIPTION_LENGTH]

    raise LinkedInJobError(
        "Could not extract a public job description from this LinkedIn page. "
        "LinkedIn may require sign-in; paste the job description manually instead.",
        422,
    )


def _canonical_job_url(job_url: str) -> str:
    try:
        parsed_url = urlsplit(job_url.strip())
        port = parsed_url.port
    except ValueError as exc:
        raise LinkedInJobError("Enter a valid LinkedIn job link.") from exc

    if (
        parsed_url.scheme != "https"
        or parsed_url.hostname not in {"linkedin.com", "www.linkedin.com"}
        or port not in (None, 443)
        or parsed_url.username
        or parsed_url.password
    ):
        raise LinkedInJobError("Enter a public link from https://www.linkedin.com.")

    match = JOB_PATH_PATTERN.fullmatch(parsed_url.path)
    if not match:
        raise LinkedInJobError("Enter a LinkedIn link to a specific job posting.")

    return f"https://www.linkedin.com/jobs/view/{match.group(1)}/"


def fetch_linkedin_job_description(job_url: str) -> str:
    canonical_url = _canonical_job_url(job_url)

    try:
        with httpx.Client(timeout=15.0, follow_redirects=False) as client:
            with client.stream(
                "GET",
                canonical_url,
                headers={"Accept": "text/html"},
            ) as response:
                if response.status_code != 200:
                    raise LinkedInJobError(
                        "LinkedIn could not provide this public job page. "
                        "It may require sign-in or may no longer be available; "
                        "paste the job description manually instead.",
                        422,
                    )

                content_type = response.headers.get("content-type", "").lower()
                if "text/html" not in content_type:
                    raise LinkedInJobError(
                        "LinkedIn returned an unexpected response for this job link.",
                        502,
                    )

                content_length = response.headers.get("content-length")
                if content_length:
                    try:
                        if int(content_length) > MAX_JOB_PAGE_BYTES:
                            raise LinkedInJobError("The LinkedIn job page is too large to read.")
                    except ValueError:
                        pass

                content = bytearray()
                for chunk in response.iter_bytes():
                    content.extend(chunk)
                    if len(content) > MAX_JOB_PAGE_BYTES:
                        raise LinkedInJobError("The LinkedIn job page is too large to read.")
    except httpx.TimeoutException as exc:
        raise LinkedInJobError(
            "Timed out while retrieving the LinkedIn job. Please try again.",
            502,
        ) from exc
    except httpx.HTTPError as exc:
        raise LinkedInJobError(
            "Could not retrieve the LinkedIn job. Please try again later.",
            502,
        ) from exc

    return _extract_job_description(content.decode("utf-8", errors="replace"))
