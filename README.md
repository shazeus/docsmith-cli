<p align="center">
  <h1 align="center">Docsmith</h1>
  <p align="center">Documentation generator, converter, inspector, and preview server for developer docs.</p>
  <p align="center">
    <a href="https://pypi.org/project/docsmith-cli/"><img alt="PyPI" src="https://img.shields.io/pypi/v/docsmith-cli.svg"></a>
    <a href="https://pypi.org/project/docsmith-cli/"><img alt="Python" src="https://img.shields.io/pypi/pyversions/docsmith-cli.svg"></a>
    <a href="LICENSE"><img alt="License" src="https://img.shields.io/badge/license-MIT-green.svg"></a>
    <a href="https://github.com/shazeus/docsmith-cli/stargazers"><img alt="Stars" src="https://img.shields.io/github/stars/shazeus/docsmith-cli.svg?style=social"></a>
  </p>
</p>

---

Docsmith is a terminal-first documentation toolkit for projects that need clean Markdown-to-site publishing without a heavy static-site framework. It can scaffold documentation, scan and validate existing docs, render a static HTML site, convert files between Markdown, HTML, text, JSON, and PDF, search content, extract outlines, and serve a local preview through Flask.

- **Static site builder** - Render Markdown or HTML docs into a responsive documentation site with navigation and copied assets.
- **Format conversion** - Convert documentation files to HTML, Markdown, text, JSON metadata, or a lightweight text PDF.
- **Schema-style inspection** - Summarize files, line counts, word counts, headings, links, and checksums in Rich tables or JSON.
- **Validation checks** - Detect broken local links, duplicate heading anchors, and Markdown files without headings.
- **Fast preview server** - Serve generated docs locally with a minimal Flask app.
- **Search and outline tools** - Locate content across a docs tree and inspect heading structure from the terminal.

## Installation

```bash
pip install docsmith-cli
```

## Usage

Create a starter documentation folder:

```bash
docsmith init docs --title "My Project Docs"
```

Inspect and validate the documentation tree:

```bash
docsmith scan docs
docsmith validate docs
```

Build a static site and serve it locally:

```bash
docsmith build docs --out site
docsmith serve docs --port 8080
```

Convert a Markdown file:

```bash
docsmith convert docs/index.md --to html --out build/index.html
docsmith convert docs/index.md --to pdf
```

## Commands

| Command | Description |
| --- | --- |
| `docsmith init <path>` | Create a starter documentation scaffold. |
| `docsmith scan <path>` | Inspect documentation files and summarize size, headings, links, and checksums. |
| `docsmith build <path>` | Build a static HTML documentation site. |
| `docsmith convert <file> --to <format>` | Convert docs to HTML, Markdown, text, JSON, or PDF. |
| `docsmith validate <path>` | Check broken local links, duplicate heading anchors, and missing headings. |
| `docsmith outline <file>` | Display a heading outline for one documentation file. |
| `docsmith search <path> <query>` | Search documentation content. |
| `docsmith serve <path>` | Start a local Flask preview server. |

## Configuration

Docsmith works without configuration. The CLI accepts explicit paths and output flags for each command. A typical project layout is:

```text
docs/
  index.md
  guide.md
  reference.md
site/
  index.html
  assets/docsmith.css
```

Use `--json-output` with `scan` or `outline` when integrating Docsmith into CI or project automation.

## License

MIT License. See [LICENSE](LICENSE).

