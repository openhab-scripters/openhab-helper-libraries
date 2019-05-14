import core
from core.log import logging, LOG_PREFIX
from org.openhab.core import OpenHAB

log = logging.getLogger(LOG_PREFIX + ".core")

def scriptLoaded(*args):
    log.info("openhab2-jython version: {}".format(core.__version__))
    if not core.openhab_support(OpenHAB.getVersion(), OpenHAB.buildString()):
        log.warn("OpenHAB in version '{}' is not fully supported by openhab2-jython-{}".format(
            OpenHAB.getVersion(), core.__version__))
