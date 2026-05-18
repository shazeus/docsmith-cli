from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


DOC_EXTENSIONS = {".md", ".markdown", ".rst", ".txt", ".html", ".htm"}
MARKDOWN_EXTENSIONS = {".md", ".markdown"}


@dataclass(frozen=True)
class DocFile:
    path: Path
    root: Path
    text: str

    @property
    def relative(self) -> Path:
        try:
            return self.path.relative_to(self.root)
        except ValueError:
            return Path(self.path.name)

    @property
    def slug(self) -> str:
        return slugify(self.relative.with_suffix("").as_posix())

    @property
    def checksum(self) -> str:
        return hashlib.sha256(self.text.encode("utf-8")).hexdigest()[:12]


def slugify(value: str) -> str:
    value = value.strip().lower().replace("\\", "/")
    value = re.sub(r"[^a-z0-9/_-]+", "-", value)
    value = re.sub(r"-{2,}", "-", value)
    value = value.strip("-/")
    return value or "index"


def ensure_path(path: str | Path) -> Path:
    candidate = Path(path).expanduser()
    if not candidate.exists():
        raise FileNotFoundError(f"{candidate} does not exist")
    return candidate.resolve()


def discover_docs(path: str | Path) -> list[Path]:
    root = ensure_path(path)
    if root.is_file():
        return [root] if root.suffix.lower() in DOC_EXTENSIONS else []

    ignored = {".git", ".venv", "venv", "node_modules", "__pycache__", "dist", "build", "site"}
    docs: list[Path] = []
    for item in root.rglob("*"):
        if not item.is_file():
            continue
        if any(part in ignored for part in item.parts):
            continue
        if item.suffix.lower() in DOC_EXTENSIONS:
            docs.append(item)
    return sorted(docs, key=lambda p: p.relative_to(root).as_posix())


def load_doc(path: Path, root: Path | None = None) -> DocFile:
    root_path = (root or path.parent).resolve()
    text = path.read_text(encoding="utf-8", errors="replace")
    return DocFile(path=path.resolve(), root=root_path, text=text)


def load_docs(path: str | Path) -> list[DocFile]:
    target = ensure_path(path)
    root = target.parent if target.is_file() else target
    return [load_doc(doc, root) for doc in discover_docs(target)]


def safe_write(path: str | Path, content: str, overwrite: bool = True) -> Path:
    output = Path(path).expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and not overwrite:
        raise FileExistsError(f"{output} already exists")
    output.write_text(content, encoding="utf-8")
    return output.resolve()


def copy_binary(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(source.read_bytes())


def iter_asset_files(root: Path, docs: Iterable[DocFile]) -> list[Path]:
    doc_paths = {doc.path.resolve() for doc in docs}
    assets: list[Path] = []
    for item in root.rglob("*"):
        if not item.is_file():
            continue
        if item.resolve() in doc_paths:
            continue
        if item.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".css", ".js"}:
            assets.append(item)
    return assets

