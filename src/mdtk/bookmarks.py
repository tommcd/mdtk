"""Convert Chrome bookmarks to markdown format."""

from bs4 import BeautifulSoup
from pathlib import Path
from typing import Optional

class BookmarkError(Exception):
    """Base exception for bookmark conversion errors."""
    pass

def convert_bookmarks(input_file: Path, output_file: Path, folder_name: Optional[str] = "EXPORT_FOLDER") -> None:
    """Convert Chrome bookmarks HTML file to markdown format."""
    # Validate inputs
    if not isinstance(input_file, Path):
        input_file = Path(input_file)
    if not isinstance(output_file, Path):
        output_file = Path(output_file)

    # Check if input file exists and is readable
    if not input_file.exists():
        raise BookmarkError(f"Input file not found: {input_file}")
    if not input_file.is_file():
        raise BookmarkError(f"Not a file: {input_file}")

    # Check if output directory exists and is writable
    if not output_file.parent.exists():
        raise BookmarkError(f"Output directory does not exist: {output_file.parent}")

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
    except Exception as e:
        raise BookmarkError(f"Failed to parse HTML file: {e}")

    # Find target folder
    folders = soup.find_all('h3')
    target_folder = None
    for folder in folders:
        if folder.string == folder_name:
            target_folder = folder
            break

    if not target_folder:
        raise BookmarkError(f"Folder '{folder_name}' not found!")

    try:
        bookmarks_dl = target_folder.find_next('dl')
        if not bookmarks_dl:
            raise BookmarkError(f"No bookmarks found in folder '{folder_name}'")
        bookmarks = bookmarks_dl.find_all('a')

        with open(output_file, 'w', encoding='utf-8') as f:
            for bookmark in bookmarks:
                title = bookmark.string or "Untitled"
                url = bookmark.get('href', '')
                f.write(f"- [{title}]({url})\n")
    except Exception as e:
        raise BookmarkError(f"Failed to process bookmarks: {e}")

def main():
    """Command line interface."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Convert Chrome bookmarks to markdown format"
    )
    parser.add_argument(
        'input_file',
        help="Chrome bookmarks HTML file"
    )
    parser.add_argument(
        'output_file',
        help="Output markdown file"
    )
    parser.add_argument(
        '--folder',
        default="EXPORT_FOLDER",
        help="Folder name to extract (default: EXPORT_FOLDER)"
    )

    args = parser.parse_args()

    try:
        convert_bookmarks(args.input_file, args.output_file, args.folder)
    except BookmarkError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
