"""Test suite for bookmarks conversion."""

import sys

import pytest

from mdtk.bookmarks import BookmarkError, convert_bookmarks, main

CHROME_EXPORT = """<!DOCTYPE NETSCAPE-Bookmark-file-1>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1>
<DL><p>
    <DT><H3 ADD_DATE="1700000000" LAST_MODIFIED="1700000001">EXPORT_FOLDER</H3>
    <DL><p>
        <DT><A HREF="https://github.com" ADD_DATE="1700000002">
        GitHub - Where the world builds software</A>
        <DT><A HREF="https://python.org">Welcome to Python.org</A>
    </DL><p>
    <DT><H3>Other Folder</H3>
    <DL><p>
        <DT><A HREF="https://example.com">Example Domain</A>
    </DL><p>
</DL><p>"""


@pytest.fixture
def bookmarks_file(tmp_path):
    """Create a realistic Chrome bookmarks export."""
    test_file = tmp_path / "bookmarks.html"
    test_file.write_text(CHROME_EXPORT, encoding="utf-8")
    return test_file


def write_export(tmp_path, body):
    test_file = tmp_path / "bookmarks.html"
    test_file.write_text(body, encoding="utf-8")
    return test_file


def test_basic_conversion(bookmarks_file, tmp_path):
    """Convert the default folder of a realistic export."""
    test_md = tmp_path / "output.md"

    count = convert_bookmarks(bookmarks_file, test_md)

    content = test_md.read_text(encoding="utf-8").strip().split("\n")
    assert count == 2
    assert len(content) == 2
    assert "- [GitHub - Where the world builds software](https://github.com)" in content
    assert "- [Welcome to Python.org](https://python.org)" in content


def test_selects_named_folder(bookmarks_file, tmp_path):
    """--folder selects a folder other than the default."""
    test_md = tmp_path / "output.md"

    count = convert_bookmarks(bookmarks_file, test_md, "Other Folder")

    assert count == 1
    assert (
        test_md.read_text(encoding="utf-8")
        == "- [Example Domain](https://example.com)\n"
    )


def test_nonexistent_folder_lists_available(bookmarks_file, tmp_path):
    """A missing folder reports which folders the export does contain."""
    with pytest.raises(BookmarkError, match="Folder 'NonExistent' not found") as exc:
        convert_bookmarks(bookmarks_file, tmp_path / "output.md", "NonExistent")

    assert "Available folders: 'EXPORT_FOLDER', 'Other Folder'" in str(exc.value)


def test_input_without_folders_is_reported(tmp_path):
    """Non-export input (e.g. Chrome's JSON bookmarks file) gets a clear error."""
    src = write_export(tmp_path, '{"roots": {"bookmark_bar": {"children": []}}}')

    with pytest.raises(BookmarkError, match="No bookmark folders found"):
        convert_bookmarks(src, tmp_path / "output.md")


def test_folder_without_list_does_not_leak_next_folder(tmp_path):
    """A folder with no <dl> of its own must not export a later folder's bookmarks."""
    src = write_export(
        tmp_path,
        """<DL><p>
    <DT><H3>EXPORT_FOLDER</H3>
    <DT><H3>Private stuff</H3>
    <DL><p>
        <DT><A HREF="https://secret.example">Should never appear</A>
    </DL><p>
</DL><p>""",
    )
    out = tmp_path / "output.md"

    with pytest.raises(BookmarkError, match="has no bookmark list"):
        convert_bookmarks(src, out, "EXPORT_FOLDER")

    assert not out.exists()


def test_empty_folder_writes_empty_file(tmp_path):
    """An empty folder converts to an empty file and reports zero bookmarks."""
    src = write_export(
        tmp_path,
        """<DL><p>
    <DT><H3>EXPORT_FOLDER</H3>
    <DL><p>
    </DL><p>
</DL><p>""",
    )
    out = tmp_path / "output.md"

    count = convert_bookmarks(src, out)

    assert count == 0
    assert out.read_text(encoding="utf-8") == ""


def test_nested_subfolders_are_flattened(tmp_path):
    """Bookmarks inside subfolders are included, flattened in document order."""
    src = write_export(
        tmp_path,
        """<DL><p>
    <DT><H3>EXPORT_FOLDER</H3>
    <DL><p>
        <DT><A HREF="https://a.example">Top level</A>
        <DT><H3>Subfolder</H3>
        <DL><p>
            <DT><A HREF="https://b.example">Inside subfolder</A>
        </DL><p>
    </DL><p>
</DL><p>""",
    )
    out = tmp_path / "output.md"

    count = convert_bookmarks(src, out)

    assert count == 2
    assert out.read_text(encoding="utf-8") == (
        "- [Top level](https://a.example)\n- [Inside subfolder](https://b.example)\n"
    )


def test_title_with_markup_is_preserved(tmp_path):
    """Inline markup in a title must not collapse it to 'Untitled'."""
    src = write_export(
        tmp_path,
        """<DL><p>
    <DT><H3>EXPORT_FOLDER</H3>
    <DL><p>
        <DT><A HREF="https://x.example">Title with <b>bold</b> markup</A>
    </DL><p>
</DL><p>""",
    )
    out = tmp_path / "output.md"

    convert_bookmarks(src, out)

    assert out.read_text(encoding="utf-8") == (
        "- [Title with bold markup](https://x.example)\n"
    )


def test_markdown_special_characters_are_escaped(tmp_path):
    """Brackets in titles and parentheses in URLs must not break the link."""
    src = write_export(
        tmp_path,
        """<DL><p>
    <DT><H3>EXPORT_FOLDER</H3>
    <DL><p>
        <DT><A HREF="https://en.wikipedia.org/wiki/Bracket_(mathematics)">
        Bracket (mathematics) [Wikipedia]</A>
    </DL><p>
</DL><p>""",
    )
    out = tmp_path / "output.md"

    convert_bookmarks(src, out)

    assert out.read_text(encoding="utf-8") == (
        r"- [Bracket (mathematics) \[Wikipedia\]]"
        "(https://en.wikipedia.org/wiki/Bracket_%28mathematics%29)\n"
    )


def test_url_brackets_encoded_outside_ipv6_host(tmp_path):
    """Brackets in path/query are encoded; IPv6 host brackets are preserved."""
    src = write_export(
        tmp_path,
        """<DL><p>
    <DT><H3>EXPORT_FOLDER</H3>
    <DL><p>
        <DT><A HREF="https://x.example/api?tags[]=python">PHP-style query</A>
        <DT><A HREF="http://[2001:db8::1]:8080/status[1]">Router status</A>
    </DL><p>
</DL><p>""",
    )
    out = tmp_path / "output.md"

    convert_bookmarks(src, out)

    assert out.read_text(encoding="utf-8") == (
        "- [PHP-style query](https://x.example/api?tags%5B%5D=python)\n"
        "- [Router status](http://[2001:db8::1]:8080/status%5B1%5D)\n"
    )


def test_bookmark_without_text_is_untitled(tmp_path):
    src = write_export(
        tmp_path,
        """<DL><p>
    <DT><H3>EXPORT_FOLDER</H3>
    <DL><p>
        <DT><A HREF="https://x.example"></A>
    </DL><p>
</DL><p>""",
    )
    out = tmp_path / "output.md"

    convert_bookmarks(src, out)

    assert out.read_text(encoding="utf-8") == "- [Untitled](https://x.example)\n"


def test_duplicate_folder_names_first_wins(tmp_path):
    src = write_export(
        tmp_path,
        """<DL><p>
    <DT><H3>Work</H3>
    <DL><p>
        <DT><A HREF="https://first.example">First</A>
    </DL><p>
    <DT><H3>Work</H3>
    <DL><p>
        <DT><A HREF="https://second.example">Second</A>
    </DL><p>
</DL><p>""",
    )
    out = tmp_path / "output.md"

    convert_bookmarks(src, out, "Work")

    assert out.read_text(encoding="utf-8") == "- [First](https://first.example)\n"


def test_missing_input_file(tmp_path):
    with pytest.raises(BookmarkError, match="Input file not found"):
        convert_bookmarks(tmp_path / "missing.html", tmp_path / "output.md")


def test_missing_output_directory(bookmarks_file, tmp_path):
    with pytest.raises(BookmarkError, match="Output directory does not exist"):
        convert_bookmarks(bookmarks_file, tmp_path / "no_such_dir" / "output.md")


def test_cli_success(bookmarks_file, tmp_path, monkeypatch, capsys):
    out = tmp_path / "output.md"
    monkeypatch.setattr(sys, "argv", ["mdtk-bookmarks", str(bookmarks_file), str(out)])

    main()

    assert "Wrote 2 bookmarks" in capsys.readouterr().out
    assert out.read_text(encoding="utf-8").count("- [") == 2


def test_cli_error_exits_nonzero(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(
        sys,
        "argv",
        ["mdtk-bookmarks", str(tmp_path / "missing.html"), str(tmp_path / "out.md")],
    )

    with pytest.raises(SystemExit) as exc:
        main()

    assert exc.value.code == 1
    assert "Error: Input file not found" in capsys.readouterr().err


def test_cli_version(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["mdtk-bookmarks", "--version"])

    with pytest.raises(SystemExit) as exc:
        main()

    assert exc.value.code == 0
    assert capsys.readouterr().out.startswith("mdtk-bookmarks ")
