"""Test suite for bookmarks conversion."""

import pytest

from mdtk.bookmarks import BookmarkError, convert_bookmarks


@pytest.fixture
def test_bookmarks_file(tmp_path):
    """Create a test bookmarks file."""
    bookmarks_content = """<!DOCTYPE NETSCAPE-Bookmark-file-1>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1>
<DL><p>
    <DT><H3>EXPORT_FOLDER</H3>
    <DL><p>
        <DT><A HREF="https://github.com">GitHub - Where the world builds software</A>
        <DT><A HREF="https://python.org">Welcome to Python.org</A>
    </DL><p>
    <DT><H3>Other Folder</H3>
    <DL><p>
        <DT><A HREF="https://example.com">Example Domain</A>
    </DL><p>
</DL><p>"""

    test_file = tmp_path / "test_bookmarks.html"
    test_file.write_text(bookmarks_content)
    return test_file


def test_basic_conversion(test_bookmarks_file, tmp_path):
    """Test basic bookmark conversion with default folder."""
    test_md = tmp_path / "output.md"

    convert_bookmarks(test_bookmarks_file, test_md)

    content = test_md.read_text().strip().split("\n")
    assert len(content) == 2
    assert "- [GitHub - Where the world builds software](https://github.com)" in content
    assert "- [Welcome to Python.org](https://python.org)" in content


def test_nonexistent_folder(test_bookmarks_file, tmp_path):
    """Test error handling for non-existent folder."""
    test_md = tmp_path / "output.md"

    with pytest.raises(BookmarkError, match="Folder 'NonExistent' not found"):
        convert_bookmarks(test_bookmarks_file, test_md, "NonExistent")
