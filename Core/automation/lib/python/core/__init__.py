# This check for the existence of 'scope' and verifying it is not a mock.Mock
# instance are needed for Sphinx autodoc because it tries to search all attrs
import mock
from core import jsr223

if hasattr(jsr223, 'scope') and not isinstance(jsr223.scope, mock.Mock):

    from core.jsr223.scope import items

    #
    # Add an attribute-resolver to the items map
    #

    def _item_getattr(self, name):
        return self[name]

    if items:# this check prevents errors if no Items have been created yet
        type(items).__getattr__ = _item_getattr.__get__(items, type(items))
