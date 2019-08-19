"""
Like the goddess of the dawn, Eos will bring light to your home with intuitive
control and custom scenes.

:author: `Michael Murton <https://github.com/CrazyIvan359>`_
:version: **0.9.0**

Change Log
----------

    **0.9.0**
        Initial Beta Release
"""

from core.log import logging, LOG_PREFIX
log = logging.getLogger("{prefix}.community.eos".format(prefix=LOG_PREFIX))

from community.eos.update import update_eos

__all__ = [ "update_eos" ]

__version__ = "0.9.0"
