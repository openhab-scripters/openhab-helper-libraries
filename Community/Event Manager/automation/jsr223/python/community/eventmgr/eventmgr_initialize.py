"""
:Author: `mr-eskildsen <https://github.com/mr-eskildsen>`_

This script must be called to ensure library is initialised.


"""
from community.eventmgr.manager import EventManager

def scriptLoaded(id):
	EventManager().getInstance()	# Force instantiation