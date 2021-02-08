__all__ = [
    "when",
    "CronTrigger",
    "ItemStateUpdateTrigger",
    "ItemStateChangeTrigger",
    "ItemCommandTrigger",
    "ThingStatusUpdateTrigger",
    "ThingStatusChangeTrigger",
    "ChannelEventTrigger",
    "GenericEventTrigger",
    "ItemEventTrigger",
    "ThingEventTrigger",
    "StartupTrigger",
    "DirectoryEventTrigger",
]

import typing as t

from java.nio.file import WatchEvent, Path

try:
    from org.openhab.core.automation import Trigger
    from org.openhab.core.events import Event
except:
    from org.eclipse.smarthome.core.automation import Trigger
    from org.eclipse.smarthome.core.events import Event

_ReturnType = t.TypeVar("_ReturnType")

def when(
    target: str,
) -> t.Callable[[t.Callable[[Event], _ReturnType]], _ReturnType]: ...

class CronTrigger(Trigger):
    trigger: t.ClassVar[Trigger]
    def __init__(
        self, cron_expression: str, trigger_name: t.Optional[str] = ...
    ) -> None: ...

class ItemStateUpdateTrigger(Trigger):
    trigger: t.ClassVar[Trigger]
    def __init__(
        self,
        item_name: str,
        state: t.Optional[str] = ...,
        trigger_name: t.Optional[str] = ...,
    ) -> None: ...

class ItemStateChangeTrigger(Trigger):
    trigger: t.ClassVar[Trigger]
    def __init__(
        self,
        item_name: str,
        previous_state: t.Optional[str] = ...,
        state: t.Optional[str] = ...,
        trigger_name: t.Optional[str] = ...,
    ) -> None: ...

class ItemCommandTrigger(Trigger):
    trigger: t.ClassVar[Trigger]
    def __init__(
        self,
        item_name: str,
        command: t.Optional[str] = ...,
        trigger_name: t.Optional[str] = ...,
    ) -> None: ...

class ThingStatusUpdateTrigger(Trigger):
    trigger: t.ClassVar[Trigger]
    def __init__(
        self,
        thing_uid: str,
        status: t.Optional[str] = ...,
        trigger_name: t.Optional[str] = ...,
    ) -> None: ...

class ThingStatusChangeTrigger(Trigger):
    trigger: t.ClassVar[Trigger]
    def __init__(
        self,
        thing_uid: str,
        previous_status: t.Optional[str] = ...,
        status: t.Optional[str] = ...,
        trigger_name: t.Optional[str] = ...,
    ) -> None: ...

class ChannelEventTrigger(Trigger):
    trigger: t.ClassVar[Trigger]
    def __init__(
        self,
        channel_uid: str,
        event: t.Optional[str] = ...,
        trigger_name: t.Optional[str] = ...,
    ) -> None: ...

class GenericEventTrigger(Trigger):
    trigger: t.ClassVar[Trigger]
    def __init__(
        self,
        event_source: str,
        event_types: t.Union[t.List[str], str],
        event_topic: str = ...,
        trigger_name: t.Optional[str] = ...,
    ) -> None: ...

class ItemEventTrigger(Trigger):
    trigger: t.ClassVar[Trigger]
    def __init__(
        self,
        event_types: t.Union[t.List[str], str],
        item_name: t.Optional[str] = ...,
        trigger_name: t.Optional[str] = ...,
    ) -> None: ...

class ThingEventTrigger(Trigger):
    trigger: t.ClassVar[Trigger]
    def __init__(
        self,
        event_types: t.Union[t.List[str], str],
        thing_uid: t.Optional[str] = ...,
        trigger_name: t.Optional[str] = ...,
    ) -> None: ...

class StartupTrigger(Trigger):
    trigger: t.ClassVar[Trigger]
    def __init__(
        self,
        trigger_name: t.Optional[str] = ...,
    ) -> None: ...

class DirectoryEventTrigger(Trigger):
    trigger: t.ClassVar[Trigger]
    def __init__(
        self,
        path: str,
        event_kinds: t.List[WatchEvent.Kind[Path]] = ...,
        watch_subdirectories: bool = ...,
        trigger_name: t.Optional[str] = ...,
    ) -> None: ...
