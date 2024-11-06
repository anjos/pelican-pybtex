<!--
SPDX-FileCopyrightText: Copyright © 2024 André Anjos <andre.dos.anjos@gmail.com>
SPDX-License-Identifier: MIT
-->

[![Build Status](https://img.shields.io/github/actions/workflow/status/anjos/pelican-pybtex/main.yml?branch=main)](https://github.com/anjos/pelican-pybtex/actions)
[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/anjos/pelican-pybtex/python-coverage-comment-action-data/endpoint.json&label=coverage)](https://htmlpreview.github.io/?https://github.com/anjos/pelican-pybtex/blob/python-coverage-comment-action-data/htmlcov/index.html)
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
global Jinja2 context used by Pelican with a `publications` variable.  The `publications`
variable is a list of dictionaries itself, each containing the following fields,
corresponding to individual entries in the provided compatible files:

* `label`: The formatted label (depends on the used style, but usually something like
`3`, `Ein05`, or `Einstein, 1905`).
* `key`: The pybtex (BibTeX) database key
* `year`: The year of the entry
* `html`: An HTML-formatted version of the entry
* `bibtex`: A BibTeX-formatted version of the entry, wrapped in a [pygments
HTML-formatted](https://pygments.org/docs/quickstart/) version. The pygments output
respects the settings for `PYGMENTS_RST_OPTIONS` in Pelican.

Use the following Pelican configuration key to list sources to be parsed and populate
the `publications` context:

```python
# any pybtex supported input format is accepted
PYBTEX_SOURCES = ["content/publications.bib"]
```

If files indicated on that list are present and readable, they will be loaded. Errors are
reported, but ignored during generation.  Check Pelican logs for details while building
your site.

Note that relative paths are considered with respect to the location of the setting of
`PATH` in `pelicanconf.py` (typically the `content` directory).  If `PATH` itself is
relative, it is considered relative to the location of `pelicanconf.py` itself.

### Extra fields

If you also set `PYBTEX_ADD_ENTRY_FIELDS`, then if any other field listed in this
setting will also be included *verbatim* in the dictionary of each entry. This feature
can be used, e.g., to include more URLs in a work, and then display those using a
custom template as explained later.

```python
PYBTEX_ADD_ENTRY_FIELDS = ["url", "pdf", "slides", "poster"]
```

### Formatting style

By default, `PYBTEX_FORMAT_STYLE` is set to `plain`.  You may further customize this
setting to one of the biobliography formatting styles supported by pybtex (currently
"plain", "alpha", "unsrt", and "unsrtalpha").  You may check the formatting style of
these BibTeX styles [on this
reference](https://www.overleaf.com/learn/latex/Bibtex_bibliography_styles). We
currently do not support custom bibliographic styles. Create an issue if you would like
to work on this.

### Publications page

This plugin provides a [default
`publications.html`](src/pelican/plugins/pybtex/templates/publications.html) template
that will render all publications *correctly loaded* from `PYBTEX_SOURCES`, ordered by
year, in reverse chronological order, and without BibTeX-style labels. Note that, if
there are no valid entries on `PYBTEX_SOURCES`, then a `publications.html` page is not
generated.

You may also want to override the default template, or parts of it with your own
modifications. To do so, create your own `publications.html` template, then use
`THEME_TEMPLATES_OVERRIDES` and `THEME_STATIC_PATHS` to add search paths for template
resolution.  For example, to add a short introductory text, we could override the
`before_content` block on the default template like so:

1. Create a file called `templates/publications.html` on your site sources, with the
   following (example) contents:

   ```html
   {% extends "!pybtex/publications.html" %}

   {% block before_content %}
   <p id="before-para">This will appear before the publication lists. One could use this
       to display their h-index, provide links to Google Scholar or ORCid.</p>
   {% endblock %}

   <!-- set PYBTEX_ADD_ENTRY_FIELDS = ["url", "pdf", "slides", "poster"] -->
   <!-- then, use it in your template override like so: -->
   {% block content_pybtex %}
   <div id="pybtex">
       {% for item in publications %}
       <details id="{{ item.key }}">
           <summary>[{{ item.label }}] {{ item.html }}</summary>
           <ul>
           {% for k in ("url", "pdf", "slides", "poster") %}
               {% if k in item %}<li>{{ k }}: {{ item[k] }}</li>{% endif %}
           {% endfor %}
           </ul>
       </details>
       {% endfor %}
   </div>
   {% endblock %}
   ```

2. Optionally, create a directory called `static` in which you may pour static files
   that control the look of your inserted content.
3. In `pelicanconf.py`, set:

   ```python
   THEME_TEMPLATES_OVERRIDES = ["templates"]
   # STATIC_PATHS = ["static"]  ## if you also have static files to be copied
   # PUBLICATIONS_SAVE_AS = "publications/index.html"  ## to change the default output file
   # PUBLICATIONS_URL = "publications/"  ## to change the default URL for publications
   ```

### Local bibliography in articles and pages

You may use markers such as `[@bibkey]` or `[@@bibkey]` on your articles and pages in
restructuredtext or markdown formats, to refer to bibliography entries from the
`PYBTEX_SOURCES`.  This process is similar to using BibTeX database entries in your
LaTeX sources by using the `\cite{bibkey}` command. In this case, this plugin will
replace these citations with links to a bibliography database *injected* at the end of
the article or post.

The global `PYBTEX_FORMAT_STYLE` is respected while formatting bibliographies.  You may
override the style for the current article or page using the metadata entry
`pybtex_format_style`.  The same mechanism is available for `PYBTEX_ADD_ENTRY_FIELDS`,
which can be locally overriden by `pybtex_add_entry_fields` metadata entry.

You may also add further enrich article or page metadata defining a specific
`pybtex_sources`.  In such a case, these files will be loaded respecting the same rules
as for `PYBTEX_SOURCES`. Specifically, relative paths are first searched at the location
of the article or page, and then default on using the `PATH` setting in
`pelicanconf.py`. Article and page bibliography markers will then be resolved by first
looking at entries in the local `pybtex_sources`, and then on the global
`PYBTEX_SOURCES` entry in `pelicanconf.py`.

Be aware that in case repeated citation keys are found across all bibliography
databases, **the last occurence is used** while resolving local bibliography for
articles an pages.

Finally, local bibliography formatting is controlled by the [default
`bibliography.html`](src/pelican/plugins/pybtex/templates/bibliography.html) template
that is shipped with this package.  This templates defines the contents of the
*injected* bibliography section on articles and pages. You may override this template in
a similar way to what was explained above for the global `publications.html` template,
by setting the `THEME_TEMPLATES_OVERRIDES` Pelican variable.

## Contributing

Contributions are welcome and appreciated. Every little bit helps. You can
contribute by improving the documentation, adding missing features, and fixing bugs. You
can also help out by reviewing and commenting on [existing
issues](https://github.com/anjos/pelican-pybtex/issues).

To start contributing to this plugin, review the [Contributing to
Pelican](https://docs.getpelican.com/en/latest/contribute.html) documentation, beginning
with the **Contributing Code** section.

## License

This project was inspired by the [original BibTeX
plugin](https://github.com/vene/pelican-bibtex), developed by Vlad Niculae, and
[pelican-cite plugin](https://github.com/VorpalBlade/pelican-cite), by Arvid Norlander.
This project and further modifications are licensed under the MIT license.
