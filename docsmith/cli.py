from __future__ import annotations

import json
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from . import __version__
from .files import load_docs
from .inspector import inspect_doc, search_docs, validate_docs
from .renderer import build_site, convert_file
from .server import create_app


console = Console()


def _handle_error(exc: Exception) -> None:
    console.print(f"[red]Error:[/red] {exc}")
    raise click.exceptions.Exit(1)


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, prog_name="docsmith")
def main() -> None:
    """Generate, convert, inspect, and serve documentation projects."""


@main.command()
@click.argument("path", default="docs")
@click.option("--title", default="Project Documentation", show_default=True, help="Title for the starter index page.")
@click.option("--force", is_flag=True, help="Overwrite starter files if they already exist.")
def init(path: str, title: str, force: bool) -> None:
    """Create a documentation scaffold."""
    try:
        root = Path(path).expanduser().resolve()
        root.mkdir(parents=True, exist_ok=True)
        files = {
            root / "index.md": f"# {title}\n\nWelcome to the documentation.\n\n## Overview\n\nAdd the main project overview here.\n",
            root / "guide.md": "# Guide\n\n## Installation\n\nDescribe installation steps here.\n\n## Usage\n\nAdd usage examples here.\n",
            root / "reference.md": "# Reference\n\nDocument commands, APIs, or configuration here.\n",
        }
        for target, content in files.items():
            if target.exists() and not force:
                continue
            target.write_text(content, encoding="utf-8")
        console.print(Panel.fit(f"Created documentation scaffold at [bold]{root}[/bold]", title="Docsmith"))
    except Exception as exc:
        _handle_error(exc)


@main.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--json-output", is_flag=True, help="Print machine-readable JSON.")
def scan(path: str, json_output: bool) -> None:
    """Inspect documentation files and summarize size, headings, and links."""
    try:
        docs = load_docs(path)
        rows = []
        for doc in docs:
            stats = inspect_doc(doc)
            rows.append(
                {
                    "file": doc.relative.as_posix(),
                    "lines": stats.lines,
                    "words": stats.words,
                    "headings": len(stats.headings),
                    "links": len(stats.links),
                    "checksum": stats.checksum,
                }
            )
        if json_output:
            console.print_json(json.dumps(rows))
            return
        table = Table(title="Documentation Scan")
        for column in ["File", "Lines", "Words", "Headings", "Links", "Checksum"]:
            table.add_column(column)
        for row in rows:
            table.add_row(
                row["file"],
                str(row["lines"]),
                str(row["words"]),
                str(row["headings"]),
                str(row["links"]),
                row["checksum"],
            )
        console.print(table)
    except Exception as exc:
        _handle_error(exc)


@main.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--out", "output", default="site", show_default=True, help="Output directory.")
@click.option("--clean", is_flag=True, help="Remove existing generated files in the output directory first.")
def build(path: str, output: str, clean: bool) -> None:
    """Build a static HTML documentation site."""
    try:
        site_dir, written = build_site(path, output, clean=clean)
        table = Table(title="Generated Site")
        table.add_column("Output")
        table.add_column("Files")
        table.add_row(str(site_dir), str(len(written)))
        console.print(table)
    except Exception as exc:
        _handle_error(exc)


@main.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--to", "to_format", required=True, type=click.Choice(["html", "md", "markdown", "txt", "text", "json", "pdf"]))
@click.option("--out", "output", help="Output file. Defaults to the input stem with the selected extension.")
def convert(file: str, to_format: str, output: str | None) -> None:
    """Convert a documentation file between markdown, HTML, text, JSON, and PDF."""
    try:
        target = convert_file(file, to_format, output)
        console.print(f"[green]Wrote[/green] {target}")
    except Exception as exc:
        _handle_error(exc)


@main.command()
@click.argument("path", type=click.Path(exists=True))
def validate(path: str) -> None:
    """Check local links, duplicate anchors, and basic document structure."""
    try:
        issues = validate_docs(path)
        if not issues:
            console.print("[green]No documentation issues found.[/green]")
            return
        table = Table(title="Validation Issues")
        table.add_column("Severity")
        table.add_column("File")
        table.add_column("Line", justify="right")
        table.add_column("Message")
        for issue in issues:
            color = "red" if issue.severity == "error" else "yellow"
            table.add_row(f"[{color}]{issue.severity}[/{color}]", str(issue.path), str(issue.line), issue.message)
        console.print(table)
        if any(issue.severity == "error" for issue in issues):
            raise click.exceptions.Exit(1)
    except click.exceptions.Exit:
        raise
    except Exception as exc:
        _handle_error(exc)


@main.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--json-output", is_flag=True, help="Print machine-readable JSON.")
def outline(file: str, json_output: bool) -> None:
    """Show the heading outline for a documentation file."""
    try:
        doc = load_docs(file)[0]
        headings = inspect_doc(doc).headings
        if json_output:
            console.print_json(json.dumps([heading.__dict__ for heading in headings]))
            return
        tree = Tree(doc.relative.as_posix())
        stack: list[tuple[int, Tree]] = [(0, tree)]
        for heading in headings:
            while stack and stack[-1][0] >= heading.level:
                stack.pop()
            parent = stack[-1][1] if stack else tree
            branch = parent.add(f"[bold]{heading.title}[/bold] [dim]line {heading.line}[/dim]")
            stack.append((heading.level, branch))
        console.print(tree)
    except Exception as exc:
        _handle_error(exc)


@main.command()
@click.argument("path", type=click.Path(exists=True))
@click.argument("query")
@click.option("--limit", default=25, show_default=True, help="Maximum matches to display.")
def search(path: str, query: str, limit: int) -> None:
    """Search documentation content."""
    try:
        matches = search_docs(path, query, limit=limit)
        if not matches:
            console.print("[yellow]No matches found.[/yellow]")
            return
        table = Table(title=f"Search: {query}")
        table.add_column("File")
        table.add_column("Line", justify="right")
        table.add_column("Text")
        for doc, line, text in matches:
            table.add_row(doc.relative.as_posix(), str(line), text)
        console.print(table)
    except Exception as exc:
        _handle_error(exc)


@main.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--host", default="127.0.0.1", show_default=True)
@click.option("--port", default=8000, show_default=True, type=int)
def serve(path: str, host: str, port: int) -> None:
    """Serve documentation locally with a Flask preview server."""
    try:
        app = create_app(path)
        console.print(f"[green]Serving documentation at[/green] http://{host}:{port}")
        app.run(host=host, port=port, debug=False)
    except Exception as exc:
        _handle_error(exc)


if __name__ == "__main__":
    main(sys.argv[1:])

