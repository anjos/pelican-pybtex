# SPDX-FileCopyrightText: Copyright © 2024 André Anjos <andre.dos.anjos@gmail.com>
# SPDX-License-Identifier: MIT
"""Populate generation context with a list of formatted citations."""

import datetime
import locale
import logging
import pathlib
import typing

import jinja2

import pelican.generators
import pelican.utils

from . import utils

logger = logging.getLogger(__name__)


class PybtexGenerator(pelican.generators.Generator):
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

        # validates pybtex sources
        if not isinstance(kwargs["settings"].get("PYBTEX_SOURCES", []), (list, tuple)):
            logger.error(
                f"Setting `PYBTEX_SOURCES` should be a list or tuple, not "
                f"{type(kwargs['settings']['PYBTEX_SOURCES'])}"
            )
            self.bibdata = []
        else:
            self.bibdata = utils.load(
                kwargs["settings"].get("PYBTEX_SOURCES", []), [kwargs["path"]]
            )

            if not self.bibdata:
                logger.info("`pybtex` (generator) plugin detected no entries.")
            else:
                sources = len(self.bibdata)
                entries = sum([len(k.entries) for k in self.bibdata])
                logger.info(
                    f"`pybtex` plugin detected {entries} entries spread across "
                    f"{sources} source file(s)."
                )

        # signals other interested parties on the same configuration
        from .signals import pybtex_generator_init

        pybtex_generator_init.send(self)

    def generate_context(self):
        """Populate context with a list of BibTeX publications.

        The generator context is modified to add a ``publications`` entry containing a
        list dictionaries, each corresponding to a BibTeX entry (in the declared order),
        with at least the following keys:

        * ``key``: The BibTeX database key
        * ``year``: The year of the entry
        * ``html``: An HTML-formatted version of the entry
        * ``bibtex``: An HTML-ready (pygments-highlighted) BibTeX-formatted version of
          the entry

        More keys as defined by ``PYBTEX_ADD_ENTRY_FIELDS`` may also be present in case
        they are found in the original database entry.  These fields are copied
        verbatim to this dictionary.
        """

        self.context["publications"] = utils.generate_context(
            self.bibdata,
            self.settings.get("PYBTEX_FORMAT_STYLE", "plain"),
            self.settings.get("PYBTEX_ADD_ENTRY_FIELDS", []),
            self.settings.get("PYGMENTS_RST_OPTIONS", {}),
        )

        # get the right formatting for the date
        default_timezone = self.settings.get("TIMEZONE", "UTC")
        timezone = getattr(self, "timezone", default_timezone)
        date = pelican.utils.set_date_tzinfo(datetime.datetime.now(), timezone)
        date_format = self.settings["DEFAULT_DATE_FORMAT"]
        if isinstance(date_format, tuple):
            locale_string = date_format[0]
            locale.setlocale(locale.LC_ALL, locale_string)
            date_format = date_format[1]
        locale_date = date.strftime(date_format)

        self.context["locale_date"] = locale_date

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
            return

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
