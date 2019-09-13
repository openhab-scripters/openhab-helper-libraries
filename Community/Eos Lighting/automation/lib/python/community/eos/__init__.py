"""
Like the goddess of the dawn, Eos will bring light to your home with intuitive
control and custom scenes.

:author: `Michael Murton <https://github.com/CrazyIvan359>`_
:version: **0.9.2**

    **0.9.1**
        `985a121 <https://github.com/CrazyIvan359/openhab-helper-libraries/commit/985a1218ae1db84e09a2fcbc2ede11d208fba6a5>`_

        *   *Added*: Log Eos version on startup.
        *   *Added*: Scene item changed rule. Previously only *received command*
            events would trigger a scene update and propagate the scene to
            group children. Now you can change a scene item's state and it will
            trigger a scene update, but will **not** propagate the scene change
            to group children.
        *   *Changed*: Group settings are now inheritted recursively from parent
            groups. Editor shows source group name if not current group.
        *   *Changed*: Values from ``configuration.py`` are reloaded when Eos is
            reinitialized.

    **0.9.0**
        `2c8476b <https://github.com/CrazyIvan359/openhab-helper-libraries/commit/2c8476be7a3cd6c9d9d1d843138ae8d64cde12b8>`_

        *   Initial Beta Release
"""

from core.log import logging, LOG_PREFIX
log = logging.getLogger("{prefix}.community.eos".format(prefix=LOG_PREFIX))

from community.eos.update import update_eos

__all__ = [ "update_eos" ]

__version__ = "0.9.2"
