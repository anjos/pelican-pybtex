# SPDX-FileCopyrightText: Copyright © 2026 Johannes Röttenbacher <jr-alias@posteo.de>
# SPDX-License-Identifier: MIT

# A custom pybtex formatting style, which highlights the given names in bold
from pybtex.richtext import Tag, Text
from pybtex.style.formatting.unsrt import Style as UnsrtStyle
from pybtex.style.template import FieldIsMissing, join, node, sentence

names_to_highlight = ["Andrè Ehrlich", "A. Ehrlich"]


@node
def highlight_names(children, context, role, highlight_lastnames=None, **kwargs):
    try:
        persons = context["entry"].persons[role]
    except KeyError as err:
        raise FieldIsMissing(role, context["entry"]) from err

    formatted = []
    for person in persons:
        # convert LateX to unicode using pybtex
        lastnames = person.rich_last_names
        firstnames = person.rich_first_names
        middlenames = person.rich_middle_names
        prelastnames = person.rich_prelast_names
        fullname = firstnames + middlenames + prelastnames + lastnames
        # get the full name as a string
        fullname_str = " ".join(name.render_as("text") for name in fullname)
        # construct the author text
        lastname = " ".join(lastname.render_as("text") for lastname in lastnames)
        names = firstnames + middlenames
        initials = " ".join(fn.render_as("text")[0] + "." for fn in names)
        author_text = f"{lastname}, {initials}" if initials else lastname
        # alternative name for matching first firstname + last lastname, first initial + last lastname
        try:
            match1 = " ".join(
                [firstnames[0].render_as("text"), lastnames[-1].render_as("text")]
            )
            match2 = " ".join(
                [
                    firstnames[0].render_as("text")[0] + ".",
                    lastnames[-1].render_as("text"),
                ]
            )
        except IndexError:
            # caused by persons with only a single name
            match1, match2 = "", ""

        # add bold formatting if the name can be matched
        if (
            fullname_str.lower() in highlight_lastnames
            or match1.lower() in highlight_lastnames
            or match2.lower() in highlight_lastnames
        ):
            formatted.append(Tag("strong", Text(author_text)))
        else:
            formatted.append(Text(author_text))

    return join(**kwargs)[formatted].format_data(context)


class HighlightAuthors(UnsrtStyle):
    def __init__(self, highlight_lastnames=None, **kwargs):
        super().__init__(**kwargs)
        if highlight_lastnames is None:
            highlight_lastnames = names_to_highlight

        self.highlight_lastnames = set(name.lower() for name in highlight_lastnames)  # noqa: C401

    def format_names(self, role, as_sentence=True):
        n = highlight_names(
            role,
            highlight_lastnames=self.highlight_lastnames,
            sep=", ",
            sep2=" and ",
            last_sep=", and ",
        )
        return sentence[n] if as_sentence else n
