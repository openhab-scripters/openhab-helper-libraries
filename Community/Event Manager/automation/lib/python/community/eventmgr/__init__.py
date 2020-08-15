"""
:Author: `mr-eskildsen <https://github.com/mr-eskildsen>`_
:Version: **1.0.0**

Astro service that offers event subscriptions. This software is distributed as a
community submission to the `openhab-helper-libraries <https://github.com/openhab-scripters/openhab-helper-libraries>`_.


About
-----

The module offers the possibility to subscribe to Cron and Astro events, as well as an option of defining a TimeOfDay sequence, 
which is also subscribeable. The integration to the Astro binding from jsr223 scripts. The problem with the Atro Binding in openHAB2 
is that you can have channel triggers (eg. sunrise, sunset), but the value is (obviously) first set when the trigger fires. The other 
option was to map the channel to an item (which gets initialized), and then subscribe to that item. The Event Manager handles this, 
and makes it possible to subscribe to events and also query the actual value (at any time). So all you have to do is to subscribe to a 
particular Astro Event or Cron Trigger. 


Release Notices
---------------

Below are important instructions if you are **upgrading** Event Manager from a previous version.
If you are creating a new installation, you can ignore what follows.

**PLEASE MAKE SURE THAT YOU GO THROUGH ALL STEPS BELOW WHERE IT SAYS "BREAKING CHANGE"... DON'T SKIP ANY VERSION**
    
    **Version 1.0.0**
        Initial version


.. admonition:: **Disclaimer**

    THIS SOFTWARE IS PROVIDED BY THE AUTHOR "AS IS" AND ANY EXPRESS OR IMPLIED
    WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
    MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
    EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
    SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
    TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
    PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
    LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
    NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
import weakref # Using this to prevent problems with garbage collection

from core.jsr223 import scope
from core.log import log_traceback, logging, LOG_PREFIX

scope.scriptExtension.importPreset("RuleSupport")
scope.scriptExtension.importPreset("RuleSimple")


LOG_CONTEXTNAME = '{}.eventmgr'.format(LOG_PREFIX)   #: Logcontext for EventMgr

EVENTMANAGER_LIB_VERSION = '1.0.0'   #: Version of Event Manager

