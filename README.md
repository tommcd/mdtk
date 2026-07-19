# mdtk (Markdown Toolkit)

Tools for working with markdown files.

[![PyPI version](https://img.shields.io/pypi/v/mdtk.svg)](https://pypi.org/project/mdtk/)
[![CI](https://github.com/tommcd/mdtk/actions/workflows/ci.yml/badge.svg)](https://github.com/tommcd/mdtk/actions/workflows/ci.yml)
[![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](https://tommcd.github.io/mdtk)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/tommcd/mdtk/blob/main/LICENSE)

## Installation

```bash
pip install mdtk
```

Requires Python 3.10+.

## Usage

### Chrome bookmarks to markdown

1. In Chrome, open the bookmark manager (`chrome://bookmarks`), put the links
   you want to export into one folder, and use **Export bookmarks** to save an
   HTML file.
2. Convert that folder to a markdown link list:

```bash
mdtk-bookmarks bookmarks.html links.md --folder "Reading List"
```

```console
$ cat links.md
- [GitHub - Where the world builds software](https://github.com)
- [Welcome to Python.org](https://python.org)
```

Options:

- `--folder NAME` - the bookmark folder to extract (default: `EXPORT_FOLDER`)
- `--version` - print the mdtk version and exit

Behavior notes:

- Bookmarks inside nested subfolders are included, flattened in document order.
- If several folders share the same name, the first one in the file is used.
- Titles and URLs are escaped so the generated markdown links stay valid.
- If the folder is not found, the error message lists the folders the export
  does contain.

### Python API

```python
from mdtk import BookmarkError, convert_bookmarks

count = convert_bookmarks("bookmarks.html", "links.md", folder_name="Reading List")
print(f"exported {count} bookmarks")
```

`convert_bookmarks` returns the number of bookmarks written and raises
`BookmarkError` for anything that goes wrong (missing file, unknown folder,
input that is not a bookmarks export, ...).

## Development

```bash
git clone https://github.com/tommcd/mdtk.git
cd mdtk
pip install -e ".[dev]"

pytest                # run the tests
ruff check .          # lint
ruff format --check . # formatting
tox                   # everything, on all supported Python versions
```

## Links

- [Documentation](https://tommcd.github.io/mdtk)
- [PyPI package](https://pypi.org/project/mdtk/)
- [Issue tracker](https://github.com/tommcd/mdtk/issues)
- [Changelog](https://github.com/tommcd/mdtk/releases)

## License

[MIT](https://github.com/tommcd/mdtk/blob/main/LICENSE)
