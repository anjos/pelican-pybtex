# SPDX-FileCopyrightText: Copyright © 2024 André Anjos <andre.dos.anjos@gmail.com>
# SPDX-License-Identifier: MIT
import pathlib

PATH = "content"
PYBTEX_SOURCES = ["publications.bib"]
PYBTEX_ADD_ENTRY_FIELDS = ["url", "foo"]
THEME_TEMPLATES_OVERRIDES = [pathlib.Path(__file__).parent / "templates"]
