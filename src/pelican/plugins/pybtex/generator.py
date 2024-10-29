# SPDX-FileCopyrightText: Copyright © 2024 André Anjos <andre.dos.anjos@gmail.com>
#
# SPDX-License-Identifier: MIT
"""Populate the context with a list of formatted citations.

The citations are loaded from external BibTeX files, at a configurable path. It can
generate a ``Publications'' page for academic websites.
"""

import logging
import pathlib
import typing

import jinja2
import pygments
import pygments.formatters
import pygments.lexers

import pelican.generators
import pybtex.backends.html
import pybtex.database
import pybtex.database.input.bibtex
import pybtex.database.output.bibtex
import pybtex.richtext
import pybtex.style.formatting.plain

logger = logging.getLogger(__name__)


class PublicationGenerator(pelican.generators.Generator):
    """Populate context with a list of BibTeX publications.

    Parameters
    ----------
    *args
        Positional parameters passed down base class initializer.
    **kwargs
        Keyword parameters passed down base class initializer.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # overrides template loder for **this generator** so that we can correctly
        # resolve overrides
        pelican_loader = typing.cast(jinja2.ChoiceLoader, self.env.loader)
        own_loader = jinja2.PackageLoader(__name__, "templates")
        self.env = jinja2.Environment(
            loader=jinja2.ChoiceLoader(
                loaders=[
                    *pelican_loader.loaders,
                    own_loader,
                    jinja2.PrefixLoader({"!pybtex": own_loader}),
                ]
            )
        )
        self.bibdata: list[pybtex.database.BibliographyData] = []

        bibtex_parser = pybtex.database.input.bibtex.Parser()
        for k in kwargs["settings"].get("PYBTEX_SOURCES", []):
            p = pathlib.Path(k)

            if not p.is_absolute():
                # make it relative to the site path
                p = kwargs["path"] / p

            if not p.exists():
                logger.error(f"BibTeX file `{p}` does not exist")
            else:
                try:
                    self.bibdata.append(bibtex_parser.parse_file(str(p)))
                except pybtex.database.PybtexError as e:
                    logger.warning(f"`bibtex` plugin failed to parse file `{k}`: {e}")
                    return

        if not self.bibdata:
            logger.info("`bibtex` plugin detected no entries.")
        else:
            sources = len(self.bibdata)
            entries = sum([len(k.entries) for k in self.bibdata])
            logger.info(
                f"`bibtex` plugin detected {entries} entries spread across "
                f"{sources} source file(s)."
            )

    def generate_context(self):
        """Populate context with a list of BibTeX publications.

        The generator context is modified to add a ``publications`` entry containing a
        list dictionaries, each corresponding to a BibTeX entry (in the declared order),
        with the following keys:

        * ``key``: The BibTeX database key
        * ``year``: The year of the entry
        * ``html``: An HTML-formatted version of the entry
        * ``bibtex``: A BibTeX-formatted version of the entry
        * ``pdf``: set if present on the BibTeX entry verbatim
        * ``slides``: set if present on the BibTeX entry verbatim
        * ``poster``: set if present on the BibTeX entry verbatim
        """

        # format entries
        plain_style = pybtex.style.formatting.plain.Style()
        html_backend = pybtex.backends.html.Backend()

        entries: list[
            tuple[str, pybtex.database.Entry, pybtex.style.FormattedEntry]
        ] = []
        for k in self.bibdata:
            entries += zip(  # noqa: B905
                k.entries.keys(),
                k.entries.values(),
                plain_style.format_bibliography(k),
            )

        publications = []
        for key, entry, text in entries:
            # make entry text, and then pass it through pygments for highlighting
            bibtex = pybtex.database.BibliographyData(entries={key: entry}).to_string(
                "bibtex"
            )
            bibtex_html = pygments.highlight(
                bibtex,
                pygments.lexers.BibTeXLexer(),
                pygments.formatters.HtmlFormatter(),
            )

            assert entry.fields is not None

            extra_fields = {
                k: v
                for k, v in entry.fields.items()
                if k in self.settings.get("PYBTEX_ADD_ENTRY_FIELDS", [])
            }

            publications.append(
                {
                    "key": key,
                    "year": entry.fields.get("year"),
                    "html": text.text.render(html_backend),
                    "bibtex": bibtex_html,
                }
            )

            publications[-1].update(extra_fields)

        self.context["publications"] = publications
        self.context["now"] = __import__("datetime").datetime.now()

    def generate_output(self, writer):
        """Generate a publication list on the website.

        This method mimics Pelican's
        :py:func:`pelican.generators.Generator.generate_direct_templates`.

        Parameters
        ----------
        writer
            The pelican writer to use.
        """

        template = "publications"

        if not self.bibdata:
            logger.info(f"Not generating `{template}.html` (no entries)")

        save_as = self.settings.get(f"{template.upper()}_SAVE_AS", f"{template}.html")
        url = self.settings.get(f"{template.upper()}_URL", f"{template}.html")

        writer.write_file(
            save_as,
            self.get_template(template),
            self.context,
            blog=True,
            template_name=template,
            page_name=pathlib.Path(save_as).stem,
            url=url,
            relative_urls=self.settings["RELATIVE_URLS"],
        )
