# SPDX-FileCopyrightText: Copyright © 2024 André Anjos <andre.dos.anjos@gmail.com>
#
# SPDX-License-Identifier: MIT

import logging
import pathlib
import typing

import pytest


@pytest.fixture
def data_path(request, subdir: str) -> pathlib.Path:
    """Return the directory in which the test is sitting. Check the pytest
    documentation for more information.

    Parameters
    ----------
    request
        Information of the requesting test function.
    subdir
        A subdirectory to return from the "data" path.

    Returns
    -------
    pathlib.Path
        The directory in which the test is sitting.
    """

    return pathlib.Path(request.module.__file__).parents[0] / "data" / subdir


@pytest.fixture
def setup_pelican(
    caplog,
    tmp_path,
    data_path,
) -> tuple[list[logging.LogRecord], pathlib.Path]:
    """Set up and teardown of pelican instance for tests.

    Parameters
    ----------
    caplog
        Pytest :std:fixture:`caplog` fixture.
    tmp_path
        Pytest :std:fixture:`tmp_path` fixture.
    data_path
        A fixutre providing access to the current project's test data path. See
        :py:func:`data_path` for details.

    Returns
    -------
        A tuple containing the captured log records during setup and build of Pelican,
        and the output path containing the built website.
    """

    from pelican import Pelican
    from pelican.log import FatalLogger
    from pelican.settings import read_settings

    content_path = data_path / "content"

    settings = {
        "SITEURL": "https://example.com",
        "TIMEZONE": "UTC",
        "THEME": "simple",
        "PATH": content_path,
        "OUTPUT_PATH": tmp_path,
        # disables generation of all indexes except the main one
        "DIRECT_TEMPLATES": ["index"],
        # disables feed generation
        "FEED_ALL_ATOM": None,
        "CATEGORY_FEED_ATOM": None,
        "TRANSLATION_FEED_ATOM": None,
        "AUTHOR_FEED_ATOM": None,
        "AUTHOR_FEED_RSS": None,
    }

    if content_path.glob("*.bib"):
        settings["PYBTEX_SOURCES"] = [k.name for k in content_path.glob("*.bib")]

    if (data_path / "templates").exists():
        settings["THEME_TEMPLATES_OVERRIDES"] = [data_path / "templates"]

    caplog.set_level(logging.INFO)

    # pelican overrides the default logging class to `pelican.log.FatalLogger`, which
    # includes a de-duplication filter.  Subsequent identical messages are
    # automoatically suppressed. The next line disables the suppression.
    typing.cast(
        FatalLogger, logging.getLogger("pelican.plugins.pybtex.generator")
    ).disable_filter()

    if (data_path / "pelicanconf.py").exists():
        pelican = Pelican(
            settings=read_settings(data_path / "pelicanconf.py", override=settings)
        )
    else:
        pelican = Pelican(settings=read_settings(override=settings))
    pelican.run()

    return caplog.records, tmp_path
