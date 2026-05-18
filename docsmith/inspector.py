from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .files import DocFile, MARKDOWN_EXTENSIONS, load_docs, slugify


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$", re.MULTILINE)
LINK_RE = re.compile(r"!?\[([^\]]*)\]\(([^)]+)\)")
WORD_RE = re.compile(r"[A-Za-z0-9_']+")


@dataclass(frozen=True)
class Heading:
    level: int
    title: str
    anchor: str
    line: int


@dataclass(frozen=True)
class Link:
    label: str
    target: str
    line: int
    external: bool


@dataclass(frozen=True)
class DocStats:
    lines: int
    words: int
    headings: list[Heading]
    links: list[Link]
    checksum: str


@dataclass(frozen=True)
class ValidationIssue:
    path: Path
    line: int
    severity: str
    message: str


def extract_headings(text: str) -> list[Heading]:
    headings: list[Heading] = []
    for match in HEADING_RE.finditer(text):
        line = text.count("\n", 0, match.start()) + 1
        title = match.group(2).strip()
        headings.append(Heading(len(match.group(1)), title, slugify(title), line))
    return headings


def extract_links(text: str) -> list[Link]:
    links: list[Link] = []
    for match in LINK_RE.finditer(text):
        line = text.count("\n", 0, match.start()) + 1
        target = match.group(2).strip()
        external = target.startswith(("http://", "https://", "mailto:", "#"))
        links.append(Link(match.group(1).strip(), target, line, external))
    return links


def inspect_doc(doc: DocFile) -> DocStats:
    return DocStats(
        lines=len(doc.text.splitlines()),
        words=len(WORD_RE.findall(doc.text)),
        headings=extract_headings(doc.text),
        links=extract_links(doc.text),
        checksum=doc.checksum,
    )


def validate_docs(path: str | Path) -> list[ValidationIssue]:
    docs = load_docs(path)
    issues: list[ValidationIssue] = []
    seen_headings: dict[tuple[Path, str], int] = {}

    for doc in docs:
        stats = inspect_doc(doc)
        if doc.path.suffix.lower() in MARKDOWN_EXTENSIONS and not stats.headings:
            issues.append(ValidationIssue(doc.path, 1, "warning", "markdown file has no headings"))

        for heading in stats.headings:
            key = (doc.path, heading.anchor)
            if key in seen_headings:
                issues.append(
                    ValidationIssue(
                        doc.path,
                        heading.line,
                        "warning",
                        f"duplicate heading anchor '{heading.anchor}' also appears on line {seen_headings[key]}",
                    )
                )
            else:
                seen_headings[key] = heading.line

        for link in stats.links:
            if link.external:
                continue
            target = link.target.split("#", 1)[0]
            if not target:
                continue
            candidate = (doc.path.parent / target).resolve()
            if not candidate.exists():
                issues.append(ValidationIssue(doc.path, link.line, "error", f"broken local link: {link.target}"))

    return issues


def search_docs(path: str | Path, query: str, limit: int = 25) -> list[tuple[DocFile, int, str]]:
    docs = load_docs(path)
    needle = query.lower()
    results: list[tuple[DocFile, int, str]] = []
    for doc in docs:
        for index, line in enumerate(doc.text.splitlines(), start=1):
            if needle in line.lower():
                results.append((doc, index, line.strip()))
                if len(results) >= limit:
                    return results
    return results

