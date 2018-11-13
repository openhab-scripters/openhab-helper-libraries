from openhab.jsr223.scope import items

#
# Add an attribute-resolver to the items map
#

def _item_getattr(self, name):
    return self[name]

type(items).__getattr__ = _item_getattr.__get__(items, type(items))
