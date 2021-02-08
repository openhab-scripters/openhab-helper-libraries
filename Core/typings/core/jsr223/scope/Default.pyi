"""
This is the contents of the ``Default`` scope, see:
https://www.openhab.org/docs/configuration/jsr223.html#default-preset-importpreset-not-required
"""

__all__ = [
    "State",
    "Command",
    "URLEncoder",
    "File",
    "Files",
    "Path",
    "Paths",
    "IncreaseDecreaseType",
    "DECREASE",
    "INCREASE",
    "OnOffType",
    "ON",
    "OFF",
    "OpenClosedType",
    "OPEN",
    "CLOSED",
    "StopMoveType",
    "STOP",
    "MOVE",
    "UpDownType",
    "UP",
    "DOWN",
    "UnDefType",
    "NULL",
    "UNDEF",
    "RefreshType",
    "REFRESH",
    "NextPreviousType",
    "NEXT",
    "PREVIOUS",
    "PlayPauseType",
    "PLAY",
    "PAUSE",
    "RewindFastforwardType",
    "REWIND",
    "FASTFORWARD",
    "QuantityType",
    "StringListType",
    "RawType",
    "DateTimeType",
    "DecimalType",
    "HSBType",
    "PercentType",
    "PointType",
    "StringType",
    "SIUnits",
    "ImperialUnits",
    "MetricPrefix",
    "Units",
    "BinaryPrefix",
    "items",
    "ir",
    "itemRegistry",
    "things",
    "rules",
    "events",
    "actions",
    "scriptExtension",
    "se",
]

from java.io import File
from java.net import URLEncoder
from java.nio.file import Files, Path, Paths

try:
    from org.openhab.core.automation import RuleRegistry
    from org.openhab.core.automation.module.script.internal import (
        ScriptExtensionManagerWrapper,
    )
    from org.openhab.core.automation.module.script.internal.defaultscope import (
        ItemRegistryDelegate,
        ScriptBusEvent,
        ScriptThingActions
    )
    from org.openhab.core.items import ItemRegistry
    from org.openhab.core.library.unit import (
        BinaryPrefix,
        ImperialUnits,
        MetricPrefix,
        SIUnits,
        Units,
    )
    from org.openhab.core.library.types import (
        DateTimeType,
        DecimalType,
        HSBType,
        IncreaseDecreaseType,
        NextPreviousType,
        OnOffType,
        OpenClosedType,
        PercentType,
        PlayPauseType,
        PointType,
        QuantityType,
        RawType,
        RewindFastforwardType,
        StringListType,
        StringType,
        StopMoveType,
        UpDownType,
    )
    from org.openhab.core.thing import ThingRegistry
    from org.openhab.core.types import Command, RefreshType, State, UnDefType
except:
    from org.eclipse.smarthome.core.automation import RuleRegistry
    from org.eclipse.smarthome.core.automation.module.script.internal import (
        ScriptExtensionManagerWrapper,
    )
    from org.eclipse.smarthome.core.automation.module.script.internal.defaultscope import (
        ItemRegistryDelegate,
        ScriptBusEvent,
        ScriptThingActions
    )
    from org.eclipse.smarthome.core.items import ItemRegistry
    from org.eclipse.smarthome.core.library.unit import (
        BinaryPrefix,
        ImperialUnits,
        MetricPrefix,
        SIUnits,
        Units,
    )
    from org.eclipse.smarthome.core.library.types import (
        DateTimeType,
        DecimalType,
        HSBType,
        IncreaseDecreaseType,
        NextPreviousType,
        OnOffType,
        OpenClosedType,
        PercentType,
        PlayPauseType,
        PointType,
        QuantityType,
        RawType,
        RewindFastforwardType,
        StringListType,
        StringType,
        StopMoveType,
        UpDownType,
    )
    from org.eclipse.smarthome.core.thing import ThingRegistry
    from org.eclipse.smarthome.core.types import Command, RefreshType, State, UnDefType

DECREASE = IncreaseDecreaseType.DECREASE
INCREASE = IncreaseDecreaseType.INCREASE
NEXT = NextPreviousType.NEXT
PREVIOUS = NextPreviousType.PREVIOUS
ON = OnOffType.ON
OFF = OnOffType.OFF
OPEN = OpenClosedType.OPEN
CLOSED = OpenClosedType.CLOSED
PLAY = PlayPauseType.PLAY
PAUSE = PlayPauseType.PAUSE
REWIND = RewindFastforwardType.REWIND
FASTFORWARD = RewindFastforwardType.FASTFORWARD
STOP = StopMoveType.STOP
MOVE = StopMoveType.MOVE
UP = UpDownType.UP
DOWN = UpDownType.DOWN

REFRESH = RefreshType.REFRESH
NULL = UnDefType.NULL
UNDEF = UnDefType.UNDEF

actions: ScriptThingActions = ...

events: ScriptBusEvent = ...

items: ItemRegistryDelegate = ...

itemRegistry: ItemRegistry = ...
ir = itemRegistry

rules: RuleRegistry = ...

scriptExtension: ScriptExtensionManagerWrapper = ...
se = scriptExtension

things: ThingRegistry = ...
