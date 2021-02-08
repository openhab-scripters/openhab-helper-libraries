__all__ = [
    "validate_item",
    "validate_channel_uid",
    "validate_uid",
    "post_update_if_different",
    "send_command_if_different",
    "postUpdateCheckFirst",
    "sendCommandCheckFirst",
    "kw",
    "iround",
    "getItemValue",
    "getLastUpdate",
    "sendCommand",
    "postUpdate",
]

import typing as t

from java.time import LocalDateTime, ZonedDateTime

try:
    from org.openhab.core.types import Command, State
    from org.openhab.core.items import GenericItem
    from org.openhab.core.thing import ChannelUID
except:
    from org.eclipse.smarthome.core.types import Command, State
    from org.eclipse.smarthome.core.items import GenericItem
    from org.eclipse.smarthome.core.thing import ChannelUID

_K = t.TypeVar("_K")
_V = t.TypeVar("_V")
Item_T = t.TypeVar("Item_T", GenericItem)
AnyState = t.Union[
    t.Type[State], t.Type[Command], str, int, float, ZonedDateTime, LocalDateTime
]
@t.overload
def validate_item(item_or_item_name: str) -> t.Union[GenericItem, None]: ...
@t.overload
def validate_item(item_or_item_name: Item_T) -> t.Union[Item_T, None]: ...
def validate_channel_uid(
    channel_uid_or_string: t.Union[ChannelUID, str]
) -> t.Union[ChannelUID, None]: ...
def validate_uid(uid: t.Optional[str]) -> str: ...
def post_update_if_different(
    item_or_item_name: t.Union[t.Type[GenericItem], str],
    new_value: AnyState,
    sendACommand: bool = ...,
    floatPrecision: t.Optional[int] = ...,
) -> bool: ...
def send_command_if_different(
    item_or_item_name: t.Union[t.Type[GenericItem], str],
    new_value: AnyState,
    floatPrecision: t.Optional[int] = ...,
) -> bool: ...

postUpdateCheckFirst = post_update_if_different
sendCommandCheckFirst = send_command_if_different

def kw(dictionary: t.MutableMapping[_K, _V], value: _V) -> t.Union[_K, None]: ...
def iround(float_value: float) -> int: ...
def getItemValue(
    item_or_item_name: t.Union[t.Type[GenericItem], str], default_value: AnyState
) -> t.Union[AnyState, None]: ...
def getLastUpdate(
    item_or_item_name: t.Union[t.Type[GenericItem], str]
) -> ZonedDateTime: ...
def sendCommand(
    item_or_item_name: t.Union[t.Type[GenericItem], str], new_value: AnyState
) -> None: ...
def postUpdate(
    item_or_item_name: t.Union[t.Type[GenericItem], str], new_value: AnyState
) -> None: ...
