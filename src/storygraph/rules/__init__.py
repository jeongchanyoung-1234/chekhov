"""Rule packs: language-specific conventions a work can opt into.

Each pack maps a rule id to a function(Manuscript) -> list[Issue].
Contribute a new language by adding a module and registering it here.
"""
from . import ko

PACKS = {
    "ko": ko.RULES,
}
