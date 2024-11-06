# SPDX-FileCopyrightText: Copyright © 2024 André Anjos <andre.dos.anjos@gmail.com>
# SPDX-License-Identifier: MIT
"""Add references to a parsed content page."""

import logging
import pathlib
import re

import pelican
import pelican.contents
import pybtex.database

from . import utils
from .generator import PybtexGenerator

logger = logging.getLogger(__name__)

# acceptable bibtex key characters:
# https://tex.stackexchange.com/questions/408530/what-characters-are-allowed-to-use-as-delimiters-for-bibtex-keys
BIBTEX_KEY_RE = r"[!\"\$&'\(\)\*\+\-\.\/:;\<\=\>\?@\[\]\^\`\|\w]+"
CITE_RE = re.compile(rf"\[(@|&#64;)(@|&#64;)?\s*({BIBTEX_KEY_RE})\s*\]")


class PybtexInjector:
    """Injects bibliography on content objects."""

    def __init__(self):
        pass

    def init(self, generator: PybtexGenerator):
        """Initialize this injector.

        Parameters
        ----------
        generator
            Plugin generator, already loaded and pre-configured with available global
            bibliography entries.
        """
        self.generator = generator
        self.main_entries: dict[str, pybtex.database.Entry] = {
            k: v for database in generator.bibdata for k, v in database.entries.items()
        }

    def resolve_bibliography(self, content: pelican.contents.Content):
        """Resolve bibliography citations.

        Parameters
        ----------
        content
            The Pelican content object ot modify.
        """

        if not content._content:  # noqa: SLF001
            # protect against spurious content being parsed
            return

        # 1. grab all citations
        citations = CITE_RE.findall(content._content)  # noqa: SLF001
        if not citations:
            # nothing to be done
            return

        # 2. load locally declared pybtex databases
        local_entries: dict[str, pybtex.database.Entry] = {}
        if "pybtex_sources" in content.metadata:
            sources = [
                k.strip() for k in content.metadata.pop("pybtex_sources").split(",")
            ]
            if content.source_path is not None:
                search_paths = [
                    pathlib.Path(content.source_path).parent,
                ]
            else:
                search_paths = []
            search_paths.append(pathlib.Path(self.generator.settings["PATH"]))
            bibdata = utils.load(sources, search_paths)
            local_entries.update(
                {k: v for db in bibdata for k, v in db.entries.items()}
            )

        # 3. create an addressable dictionary with all citations
        all_entries = dict(self.main_entries.items())
        all_entries.update(local_entries)  # will have preference

        # 4. check all citations exist on one of the databases (global) or local
        # Resolve the ones we can by selecting those entries
        content_entries: dict[str, pybtex.database.Entry] = {}
        for citation in citations:
            key = citation[-1]
            if key in all_entries:
                content_entries[key] = all_entries[key]
            else:
                logger.error(
                    f"Cannot find pybtex key `{key}` in any of the loaded databases. "
                    f"Ignoring biobliography entry."
                )

        # 5. create a new section called "Bibliography" that contains all entries of
        # citations found on step 3
        if not content_entries:
            logger.info("Not generating content bibliography (no matching entries)")
            return

        template_name = "bibliography"
        template = self.generator.get_template(template_name)
        database = pybtex.database.BibliographyData(entries=content_entries)

        style = self.generator.settings.get("PYBTEX_FORMAT_STYLE", "plain")
        if "pybtex_format_style" in content.metadata:
            style = content.metadata.pop("pybtex_format_style").strip() or style

        add_entry_fields = self.generator.settings.get("PYBTEX_ADD_ENTRY_FIELDS", [])
        if "pybtex_add_entry_fields" in content.metadata:
            add_entry_fields = (
                content.metadata.pop("pybtex_add_entry_fields").strip()
                or add_entry_fields
            )

        context = {
            "publications": utils.generate_context(
                [database],
                style,
                add_entry_fields,
                self.generator.settings.get("PYGMENTS_RST_OPTIONS", {}),
            )
        }
        content._content += template.render(context)  # noqa: SLF001

        # 6. replace each citation with a styled marker that links to the bibliography
        # section that was created on step 5.
        lk = {k["key"]: k["label"] for k in context["publications"]}

        def _re_repl(matchobj):
            key = matchobj.groups()[-1]
            if key in lk:
                return (
                    f'<a title="click to jump to reference [{lk[key]}]"'
                    f'href="#pybtex-{key}">[{lk[key]}]</a>'
                )
            return f'<span title="cannot find citation {key}">[{key}?]</span>'

        content._content = CITE_RE.sub(_re_repl, content._content)  # noqa: SLF001
