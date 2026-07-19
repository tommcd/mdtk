"""Convert Chrome bookmarks to markdown format."""

import argparse
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from bs4 import BeautifulSoup, Tag


class BookmarkError(Exception):
    """Base exception for bookmark conversion errors."""


def _clean_text(text: str) -> str:
    """Collapse whitespace runs so titles stay on one markdown line."""
    return " ".join(text.split())


def _escape_title(text: str) -> str:
    """Escape characters that would break out of a markdown link label."""
    return text.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")


def _escape_url(url: str) -> str:
    """Percent-encode characters that would break a markdown link target."""
    for char, quoted in (
        (" ", "%20"),
        ("(", "%28"),
        (")", "%29"),
        ("<", "%3C"),
        (">", "%3E"),
    ):
        url = url.replace(char, quoted)
    return url


def _find_folder(soup: BeautifulSoup, folder_name: str) -> Tag:
    """Return the <h3> heading of the named bookmark folder."""
    folders = soup.find_all("h3")
    if not folders:
        raise BookmarkError(
            "No bookmark folders found in input - "
            "is it a bookmarks HTML export (chrome://bookmarks > Export)?"
        )
    for folder in folders:
        if _clean_text(folder.get_text()) == folder_name:
            return folder
    names = ", ".join(repr(_clean_text(f.get_text())) for f in folders)
    raise BookmarkError(f"Folder {folder_name!r} not found. Available folders: {names}")


def _find_bookmark_list(folder: Tag) -> Tag:
    """Return the <dl> element holding *folder*'s bookmarks.

    Bookmark exports place a folder's <dl> right after its <h3> heading.
    Walk forward in document order but stop at the next folder heading, so
    a folder without a list of its own raises an error instead of silently
    picking up a later folder's bookmarks.
    """
    for element in folder.next_elements:
        if not isinstance(element, Tag):
            continue
        if element.name == "dl":
            return element
        if element.name == "h3":
            break
    raise BookmarkError(
        f"Folder {_clean_text(folder.get_text())!r} has no bookmark list"
    )


def convert_bookmarks(
    input_file: Path | str,
    output_file: Path | str,
    folder_name: str = "EXPORT_FOLDER",
) -> int:
    """Convert one folder of a Chrome bookmarks HTML export to a markdown list.

    Bookmarks in nested subfolders are included, flattened in document
    order. If several folders share the same name, the first one in the
    file is used. Returns the number of bookmarks written.
    """
    input_file = Path(input_file)
    output_file = Path(output_file)

    if not input_file.exists():
        raise BookmarkError(f"Input file not found: {input_file}")
    if not input_file.is_file():
        raise BookmarkError(f"Not a file: {input_file}")
    if not output_file.parent.exists():
        raise BookmarkError(f"Output directory does not exist: {output_file.parent}")

    try:
        html = input_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        raise BookmarkError(f"Failed to read {input_file}: {e}") from e

    soup = BeautifulSoup(html, "html.parser")
    target_folder = _find_folder(soup, folder_name)
    bookmarks_dl = _find_bookmark_list(target_folder)

    lines = []
    for bookmark in bookmarks_dl.find_all("a"):
        title = _escape_title(_clean_text(bookmark.get_text())) or "Untitled"
        url = _escape_url(bookmark.get("href", ""))
        lines.append(f"- [{title}]({url})\n")

    try:
        output_file.write_text("".join(lines), encoding="utf-8")
    except OSError as e:
        raise BookmarkError(f"Failed to write {output_file}: {e}") from e

    return len(lines)


def _version() -> str:
    try:
        return version("mdtk")
    except PackageNotFoundError:
        return "unknown"


def main() -> None:
    """Command line interface."""
    parser = argparse.ArgumentParser(
        prog="mdtk-bookmarks",
        description="Convert Chrome bookmarks to markdown format",
    )
    parser.add_argument(
        "input_file", help="bookmarks HTML file (chrome://bookmarks > Export)"
    )
    parser.add_argument("output_file", help="Output markdown file")
    parser.add_argument(
        "--folder",
        default="EXPORT_FOLDER",
        help="Folder name to extract (default: EXPORT_FOLDER)",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {_version()}")

    args = parser.parse_args()

    try:
        count = convert_bookmarks(args.input_file, args.output_file, args.folder)
    except BookmarkError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    plural = "" if count == 1 else "s"
    print(f"Wrote {count} bookmark{plural} to {args.output_file}")


if __name__ == "__main__":
    main()
