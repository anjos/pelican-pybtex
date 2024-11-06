# SPDX-FileCopyrightText: Copyright © 2024 André Anjos <andre.dos.anjos@gmail.com>
# SPDX-License-Identifier: MIT
"""Monkey-patch standard style from pybtex to support some extra entry
types.
"""

from pybtex.style.formatting import toplevel
import pybtex.style.formatting.unsrt
from pybtex.style.formatting.unsrt import date
from pybtex.style.template import field, node, optional, sentence, tag, words


def _monkeypatch_method(cls):
    def decorator(func):
        setattr(cls, func.__name__, func)
        return func

    return decorator


@_monkeypatch_method(pybtex.style.formatting.unsrt.Style)
def get_patent_template(self, e):
    """Format patent bibtex entry.

    Parameters
    ----------
    e
        The entry to be formatted.

    Returns
    -------
        The formatted entry object.
    """
    return toplevel[
        sentence[self.format_names("author")],
        self.format_title(e, "title"),
        sentence(capfirst=False)[tag("em")[field("number")], date],
        optional[self.format_url(e), optional[" (visited on ", field("urldate"), ")"]],
    ]


# format month by converting integers to month name
_MONTH_NAMES = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}


@node
def _month_field(children, data):
    assert not children
    m = data["entry"].fields.get("month")
    try:
        m = int(m)
        # normalize
        m = 1 if m < 1 else m
        m = len(_MONTH_NAMES) if m > len(_MONTH_NAMES) else m
        # reset
        data["entry"].fields["month"] = _MONTH_NAMES[m]
    except (TypeError, ValueError):
        pass
    return optional[field("month")].format_data(data)


# Ensures we always have the month correctly formatted
pybtex.style.formatting.unsrt.date = words[_month_field(), field("year")]
