"""
:author: `Michael Murton <https://github.com/CrazyIvan359>`_
:version: **0.1.0**

**PREFACE**

Change Log
----------

    **0.1.0**
        Initial Release
"""

from core.log import logging, LOG_PREFIX
log = logging.getLogger("{prefix}.community.eos".format(prefix=LOG_PREFIX))

from community.eos.update import update_eos

__all__ = [ "update_eos" ]

__version__ = "0.1.0"
