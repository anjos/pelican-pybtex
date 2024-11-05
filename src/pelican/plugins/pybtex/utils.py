# SPDX-FileCopyrightText: Copyright © 2024 André Anjos <andre.dos.anjos@gmail.com>
# SPDX-License-Identifier: MIT
"""Common utilities to load and format bibliography entries."""

import importlib
import logging
import pathlib
import typing

import pygments.formatters
import pygments.lexers

import pybtex.backends.html
import pybtex.database
import pybtex.database.input.bibtex
import pybtex.style.formatting

logger = logging.getLogger(__name__)


def _resolve(name: pathlib.Path, paths: typing.Sequence[pathlib.Path]) -> pathlib.Path:
    """Search for a file named ``name`` and returns the first occurence.

    Parameters
    ----------
    name
        The name to search for - may contain folder separators.  If it is absolute, then
        the path is returned as is.
    paths
        All paths to consider when searching.

    Returns
    -------
        The path to a file that exists, or ``name`` itself, if a match cannot be found.
    """

    if name.is_absolute():
        return name

    for p in paths:
        if (p / name).exists():
            return p / name

    return name


def load(
    databases: list[str], paths: typing.Sequence[pathlib.Path]
) -> list[pybtex.database.BibliographyData]:
    """Load a list of databases from file.

    Parameters
    ----------
    databases
        List of databases to load.
    paths
        All paths to consider when searching.

    Returns
    -------
        A list of pybtex entries.
    """

    retval: list[pybtex.database.BibliographyData] = []

    bibtex_parser = pybtex.database.input.bibtex.Parser()
    for k in databases:
        p = _resolve(pathlib.Path(k), paths)

        if not p.exists():
            logger.error(
                f"`pybtex` file `{p}` cannot be found on path "
                f"`{':'.join([str(k) for k in paths])}`"
            )
        else:
            try:
                retval.append(bibtex_parser.parse_file(p))
                logger.debug(f"Loaded pybtex file `{p}`")
            except pybtex.database.PybtexError:
                logger.exception(f"`pybtex` plugin failed to parse file `{k}`")

    return retval


def format_bibtex(entry: pybtex.database.Entry) -> str:
    """Format a pybtex database entry into a BibTeX representation.

    Parameters
    ----------
    entry
        The entry to be formatted.

    Returns
    -------
        A string containing the entry in BibTeX format.
    """

    return pybtex.database.BibliographyData(entries={entry.key: entry}).to_string(
        "bibtex"
    )


def format_bibtex_pygments(
    entry: pybtex.database.Entry, html_formatter_options: dict[str, typing.Any]
) -> str:
    """Format a pybtex database entry into a highlight-able HTML/BibTeX
    representation.

    Parameters
    ----------
    entry
        The entry to be formatted.
    html_formatter_options
        A dictionary containing HTML formatting options supported by
        :py:class:`pygments.formatters.HtmlFormatter`.

    Returns
    -------
        A string containing the entry in highlight-able BibTeX format.
    """

    return pygments.highlight(
        format_bibtex(entry),
        pygments.lexers.BibTeXLexer(),
        pygments.formatters.HtmlFormatter(**html_formatter_options),
    )


def generate_context(
    bibdata: typing.Sequence[pybtex.database.BibliographyData],
    style_name: str,
    extra_fields: typing.Sequence[str],
    html_formatter_options: dict[str, typing.Any],
) -> list[dict[str, str]]:
    """Generate a list of dictionaries given a set of bibliography databases.

    Parameters
    ----------
    bibdata
        A sequence of bibliography databases, each containing multiple entries.
    style_name
        One of the biobliography formatting styles supported by pybtex (currently
        "plain", "alpha", "unsrt", and "unsrtalpha").
    extra_fields
        Extra fields to be preserved (verbatim) from each entry, if present.
    html_formatter_options
        A dictionary containing HTML formatting options supported by
        :py:class:`pygments.formatters.HtmlFormatter`.

    Returns
    -------
        A list dictionaries, each corresponding to a BibTeX entry (in the declared
        order) from the input databases. Each entry in the list contains at least the
        following keys:

            * ``key``: The BibTeX database key
            * ``year``: The year of the entry
            * ``html``: An HTML-formatted version of the entry
            * ``bibtex``: An HTML-ready (pygments-highlighted) BibTeX-formatted version of
              the entry

        More keys as defined by ``extra_fiedls`` may also be present in case they are
        found in the original database entry.  These fields are copied verbatim to this
        dictionary.
    """
    # just to avoid pyright warnings as the name of this plugin matches the name of the
    # library we are using
    import pybtex.backends.html
    import pybtex.database

    if style_name in ("plain", "alpha", "unsrt", "unsrtalpha"):
        formatter = importlib.import_module(f"pybtex.style.formatting.{style_name}")
        style = formatter.Style()
    else:
        logger.error(
            f"Unsupported formatting style `{style_name}`, defaulting to `plain`"
        )
        import pybtex.style.formatting.plain

        style = pybtex.style.formatting.plain.Style()

    # format all entries in a single shot for speed and meaningful labels
    all_entries = [e for k in bibdata for e in k.entries.values()]

    # overrides pybtex.style.formatting.Style.format_entries to avoid sorting
    formatted_entries = [
        style.format_entry(k, e)
        for k, e in zip(style.format_labels(all_entries), all_entries)
    ]

    backend = pybtex.backends.html.Backend()
    retval: list[dict[str, str]] = []
    for entry, formatted_entry in zip(all_entries, formatted_entries):
        # make entry text, and then pass it through pygments for highlighting
        assert entry.fields is not None

        retval.append(
            {
                "label": typing.cast(str, formatted_entry.label),
                "key": formatted_entry.key,
                "year": entry.fields.get("year"),
                "html": formatted_entry.text.render(backend),
                "bibtex": format_bibtex_pygments(entry, html_formatter_options),
            }
        )

        # updates entry with extra fields
        retval[-1].update({k: v for k, v in entry.fields.items() if k in extra_fields})

    return retval
