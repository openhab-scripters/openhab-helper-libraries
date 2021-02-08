"""
There is an auto-loader in `core.jsr223` that will import the neccesary
preset to get any object available in any preset, so all presets are imported
here to mimic that.
"""

from core.jsr223.scope.Default import *
from core.jsr223.scope.RuleFactories import *
from core.jsr223.scope.RuleSimple import *
from core.jsr223.scope.RuleSupport import *
