# SPDX-FileCopyrightText: Copyright © 2024 André Anjos <andre.dos.anjos@gmail.com>
#
# SPDX-License-Identifier: MIT
"""Manage your academic publications page with Pelican and pybtex (BibTeX)."""

from . import style as _  # noqa: F401, monkey-patches to support extra entries
from .injector import PybtexInjector

_injector = PybtexInjector()


def _get_generators(pelican_object):
    del pelican_object  # shuts-up linter

    from .generator import PybtexGenerator

    return PybtexGenerator


def register():
    """Register this plugin to pelican."""

    import pelican.plugins.signals

    from . import signals

    # Global bibliography page
    pelican.plugins.signals.get_generators.connect(_get_generators)

    # Per-content (articles, pages) biobliography injector
    signals.pybtex_generator_init.connect(_injector.init)
    pelican.plugins.signals.content_object_init.connect(_injector.resolve_bibliography)
