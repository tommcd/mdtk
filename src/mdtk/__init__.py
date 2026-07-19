"""mdtk (Markdown Toolkit) - Tools for working with markdown files."""

from mdtk.bookmarks import BookmarkError, convert_bookmarks

try:
    from mdtk._version import version as __version__
except ImportError:
    from importlib.metadata import PackageNotFoundError
    from importlib.metadata import version as _pkg_version

    try:
        __version__ = _pkg_version("mdtk")
    except PackageNotFoundError:
        __version__ = "0+unknown"

__all__ = ["BookmarkError", "__version__", "convert_bookmarks"]
