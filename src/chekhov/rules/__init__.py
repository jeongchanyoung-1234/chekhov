"""Rule packs: language-specific conventions a work can opt into.

Each pack maps a rule id to a function(Manuscript) -> list[Issue], and may define
aliases (one name for several rules). Contribute a new language by adding a module
and registering it here.
"""
from . import ko

PACKS = {
    "ko": ko.RULES,
}

ALIASES = {
    "ko": ko.ALIASES,
}
