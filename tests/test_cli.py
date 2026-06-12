from pathlib import Path

from click.testing import CliRunner

from docsmith.cli import main


def test_init_build_validate_and_convert_workflows(tmp_path: Path) -> None:
    runner = CliRunner()
    docs_dir = tmp_path / "docs"
    site_dir = tmp_path / "site"
    html_path = tmp_path / "index.html"

    init_result = runner.invoke(main, ["init", str(docs_dir), "--title", "My Project Docs"])
    assert init_result.exit_code == 0
    assert (docs_dir / "index.md").exists()

    validate_result = runner.invoke(main, ["validate", str(docs_dir)])
    assert validate_result.exit_code == 0
    assert "No documentation issues found." in validate_result.output

    build_result = runner.invoke(main, ["build", str(docs_dir), "--out", str(site_dir)])
    assert build_result.exit_code == 0
    assert (site_dir / "index.html").exists()

    convert_result = runner.invoke(
        main,
        ["convert", str(docs_dir / "index.md"), "--to", "html", "--out", str(html_path)],
    )
    assert convert_result.exit_code == 0
    assert html_path.exists()
    assert html_path.stat().st_size > 0


def test_outline_json_output(tmp_path: Path) -> None:
    runner = CliRunner()
    docs_dir = tmp_path / "docs"
    runner.invoke(main, ["init", str(docs_dir), "--title", "My Project Docs"])

    result = runner.invoke(main, ["outline", str(docs_dir / "index.md"), "--json-output"])

    assert result.exit_code == 0
    assert '"title": "My Project Docs"' in result.output
