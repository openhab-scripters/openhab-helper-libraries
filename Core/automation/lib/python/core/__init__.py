from core.jsr223.scope import items

#
# Add an attribute-resolver to the items map
#

def _item_getattr(self, name):
    return self[name]

type(items).__getattr__ = _item_getattr.__get__(items, type(items))

__version__="1.0.0a"

def openhab_support(version, build_number):
    """Checks if given OpenHab version is compatible with this release

    Arguments:
        version {str} -- version of OpenHab (ex. 2.4.0, 2.4.0-M2)
        build_number {str} -- build string reported by OpenHAB instance (ignored for now)

    Returns:
        True -- scripts are known to be working with this version of OH
        False -- OH version is too old or not tested, issues might arise
    """
    from pkg_resources import parse_version

    # Get rid of -SNAPSHOT or -MX suffix for 'epoch' comparison
    ver_tuple = version.split("-", 1)
    ver_epoch = parse_version(ver_tuple[0])

    return ver_epoch >= parse_version("2.4.0")
