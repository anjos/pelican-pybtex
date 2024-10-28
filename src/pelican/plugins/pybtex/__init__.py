# SPDX-FileCopyrightText: Copyright © 2024 André Anjos <andre.dos.anjos@gmail.com>
#
# SPDX-License-Identifier: MIT


def _connector(pelican_object):
    from .generator import PublicationGenerator

    return PublicationGenerator


def register():
    """Register this plugin to pelican."""

    import pelican.plugins.signals

    pelican.plugins.signals.get_generators.connect(_connector)
