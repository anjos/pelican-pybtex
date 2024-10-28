<!--
SPDX-FileCopyrightText: Copyright © 2024 André Anjos <andre.dos.anjos@gmail.com>
SPDX-License-Identifier: MIT
-->

[![Build Status](https://img.shields.io/github/actions/workflow/status/pelican-plugins/pelican-pybtex/main.yml?branch=main)](https://github.com/anjos/pelican-pybtex/actions)
[![PyPI Version](https://img.shields.io/pypi/v/pelican-pybtex)](https://pypi.org/project/pelican-pybtex/)
[![Downloads](https://img.shields.io/pypi/dm/pelican-pybtex)](https://pypi.org/project/pelican-pybtex/)
![License](https://img.shields.io/pypi/l/pelican-pybtex?color=blue)

# pybtex: A Plugin for Pelican

Organize your scientific publications with [pybtex](https://pybtex.org)
([BibTeX](https://www.bibtex.com/g/bibtex-format/)) in [Pelican](https://getpelican.com).

## Installation

This plugin can be installed via:

```sh
pip install pelican-pybtex
````

This a "namespace plugin" for Pelican.  After installation, it should be automatically
detected.  It is enabled by default if `PLUGINS` is not set on your configuration.  In
case that variable is set, add `pybtex` to the list of plugins to load. For more
information, check [How to Use
Plugins](https://docs.getpelican.com/en/latest/plugins.html#how-to-use-plugins)
documentation.

## Usage

This plugin reads a user-specified [pybtex supported
file](https://docs.pybtex.org/formats.html#bibliography-formats) and populates the
global Jinja2 context used by Pelican with a `publications` entry.  The `publications`
entry is a list containing the following fields:

* `key`: The pybtex (BibTeX) database key
* `year`: The year of the entry
* `html`: An HTML-formatted version of the entry
* `bibtex`: A BibTeX-formatted version of the entry
* `pdf`: set if present on the BibTeX entry verbatim
* `slides`: set if present on the BibTeX entry verbatim
* `poster`: set if present on the BibTeX entry verbatim

The configuration has a single entry, that lists sources parsed to populate the
`publications` context:

```python
PYBTEX_SOURCES = ["content/publications.bib"]
```

If files indicated on that list are present and readable, they will be loaded. Errors are
reported, but ignored during generation.  Check Pelican logs for details while building
your site.

Note that relative paths are considered with respect to the location of
`pelicanconf.py`.

### Publications page

This plugin provides a [default
`publications.html`](src/pelican/plugins/pybtex/templates/publications.html) template
that will render all publications *correctly loaded* from `PYBTEX_SOURCES`, ordered by
year, in reverse chronological order.

You may want to override the default template, or parts of it with your own modifications.

To do so, create your own `publications.html` template, then use
`THEME_TEMPLATES_OVERRIDES` and `THEME_STATIC_PATHS` to add search paths for template
resolution.  For example, to add a short introductory text, we could override the
`before_content` block on the default template like so:

1. Create a file called `templates/publications.html` on your site sources, with the
   following contents:

   ```html
   {% extends "!pybtex/publications.html" %}

   {% block before_content %}
   <p id="before-para">This will appear before the publication lists. One could use this
       to display their h-index, provide links to Google Scholar or ORCid.</p>
   {% endblock %}
   ```

2. Optionally, create a directory called `static` in which you may pour static files
   that control the look of your inserted content.
3. In `pelicanconf.py`, set:

   ```python
   THEME_TEMPLATES_OVERRIDES = ["templates"]
   # THEME_STATIC_PATHS = ["static"]  ## this is the default, no need to set it.
   ```

### Extending this plugin

A relatively simple but possibly useful extension is to make it possible to write
internal links in Pelican pages and blog posts that would point to the corresponding
paper in the Publications page.

A slightly more complicated idea is to support general referencing in articles and
pages, by having some pybtex entries local to the page, and rendering the bibliography
at the end of the article, with anchor links pointing to the right place.

## Contributing

Contributions are welcome and much appreciated. Every little bit helps. You can
contribute by improving the documentation, adding missing features, and fixing bugs. You
can also help out by reviewing and commenting on [existing
issues](https://github.com/anjos/pelican-pybtex/issues).

To start contributing to this plugin, review the [Contributing to
Pelican](https://docs.getpelican.com/en/latest/contribute.html) documentation, beginning
with the **Contributing Code** section.

## License

This project was inspired by the [original BibTeX
plugin](https://github.com/vene/pelican-bibtex), developed by Vlad Niculae. This project
and further modifications are licensed under the MIT license.
