# SPDX-FileCopyrightText: Copyright © 2024 André Anjos <andre.dos.anjos@gmail.com>
#
# SPDX-License-Identifier: MIT

import logging
import pathlib

from bs4 import BeautifulSoup
import pytest


def _assert_log_contains(
    records: list[logging.LogRecord], message: str, level: int, count: int = 1
) -> None:
    """Assert that the log records contains the given count of matching
    messages.

    Parameters
    ----------
    records
        All logging records collected.
    message
        The message that must be searched for.
    level
        The level of the message that must match.
    count
        The number of times the message must appear.
    """

    filtered = [k for k in records if k.levelno == level and message in k.message]

    assert len(filtered) == count, (
        f"Found {len(filtered)} records containing `{message}` at "
        f"level {level} ({logging.getLevelName(level)}) instead "
        f"of {count} (expected)."
    )


def _assert_log_no_errors(
    records: list[logging.LogRecord], level: int = logging.ERROR
) -> None:
    """Assert that the log records do not contain any message with a level
    equal or above the indicated value.

    Parameters
    ----------
    records
        All logging records collected.
    level
        The level of the message that must match.
    """

    filtered = [k for k in records if k.levelno >= level]

    assert len(filtered) == 0, (
        f"Found {len(filtered)} record(s) containing level {level} "
        f"({logging.getLevelName(level)}) at least."
    )


@pytest.mark.parametrize("subdir", ["empty"])
def test_empty(setup_pelican: tuple[list[logging.LogRecord], pathlib.Path]):
    records, pelican_output = setup_pelican

    publications_html = pelican_output / "publications.html"
    assert not publications_html.exists()

    _assert_log_no_errors(records)
    _assert_log_contains(
        records, message="plugin detected no entries", level=logging.INFO, count=1
    )


@pytest.mark.parametrize("subdir", ["simple"])
def test_simple(setup_pelican: tuple[list[logging.LogRecord], pathlib.Path]):
    records, pelican_output = setup_pelican

    publications_html = pelican_output / "publications.html"
    assert publications_html.exists()

    with publications_html.open() as f:
        soup = BeautifulSoup(f, "html.parser")

    div = soup.find_all("div", id="pybtex")
    assert len(div) == 1

    publication_keys = [
        "CitekeyArticle",
        "CitekeyBook",
        "CitekeyBooklet",
        "CitekeyInbook",
        "CitekeyIncollection",
        "CitekeyInproceedings",
        "CitekeyManual",
        "CitekeyMastersthesis",
        "CitekeyMisc",
        "CitekeyPhdthesis",
        "CitekeyProceedings",
        "CitekeyTechreport",
        "CitekeyUnpublished",
    ]
    details = div[0].find_all("details")
    assert len(details) == len(publication_keys)

    for detail in details:
        # should correspond to one of the expected entries
        assert detail.attrs["id"][len("pybtex-") :] in publication_keys

        # it should contain the bibtex entry
        pre = detail.find_all("pre")
        assert len(pre) == 1

        # check pygments filtered the BibTeX entry
        assert "highlight" in pre[0].parent.attrs["class"]

        # the bibtex entry should start with @
        assert detail.pre.text.startswith("@")

    _assert_log_no_errors(records)
    _assert_log_contains(
        records,
        message="plugin detected 13 entries spread across 1 source file",
        level=logging.INFO,
        count=1,
    )


@pytest.mark.parametrize("subdir", ["urls"])
def test_urls(setup_pelican: tuple[list[logging.LogRecord], pathlib.Path]):
    records, pelican_output = setup_pelican

    publications_html = pelican_output / "publications.html"
    assert publications_html.exists()

    with publications_html.open() as f:
        soup = BeautifulSoup(f, "html.parser")

    div = soup.find_all("div", id="pybtex")
    assert len(div) == 1

    publication_keys = [
        "entries",
        "noentries",
    ]
    details = div[0].find_all("details")
    assert len(details) == len(publication_keys)

    assert details[0].attrs["id"] == publication_keys[0]
    items = details[0].find_all("li")
    items_to_check = ["url", "foo"]
    assert len(items) == len(items_to_check)
    for i, k in enumerate(items_to_check):
        assert items[i].text.startswith(k + ":")

    assert details[1].attrs["id"] == publication_keys[1]
    items = details[1].find_all("li")
    assert len(items) == 0

    for detail in details:
        # should correspond to one of the expected entries
        assert detail.attrs["id"] in publication_keys

    _assert_log_no_errors(records)
    _assert_log_contains(
        records,
        message="plugin detected 2 entries spread across 1 source file",
        level=logging.INFO,
        count=1,
    )


@pytest.mark.parametrize("subdir", ["override"])
def test_override(setup_pelican: tuple[list[logging.LogRecord], pathlib.Path]):
    records, pelican_output = setup_pelican

    publications_html = pelican_output / "publications.html"
    assert publications_html.exists()

    with publications_html.open() as f:
        soup = BeautifulSoup(f, "html.parser")

    para = soup.find_all("p", id="before-para")
    assert len(para) == 1
    assert para[0].text.startswith("This will appear before the publication lists.")

    div = soup.find_all("div", id="pybtex")
    assert len(div) == 1

    _assert_log_no_errors(records)
    _assert_log_contains(
        records,
        message="plugin detected 2 entries spread across 1 source file",
        level=logging.INFO,
        count=1,
    )


@pytest.mark.parametrize("subdir", ["biblio1"])
def test_biblio1(setup_pelican: tuple[list[logging.LogRecord], pathlib.Path]):
    records, pelican_output = setup_pelican

    article_html = pelican_output / "article.html"
    assert article_html.exists()

    publications_html = pelican_output / "publications.html"
    assert not publications_html.exists()

    # with article_html.open() as f:
    #     soup = BeautifulSoup(f, "html.parser")

    _assert_log_no_errors(records)
    _assert_log_contains(
        records, message="plugin detected no entries", level=logging.INFO, count=1
    )
