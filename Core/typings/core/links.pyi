import typing as t

try:
    from org.openhab.core.items import GenericItem
    from org.openhab.core.thing import ChannelUID
except:
    from org.eclipse.smarthome.core.items import GenericItem
    from org.eclipse.smarthome.core.thing import ChannelUID


Item_T = t.TypeVar("Item_T", bound=GenericItem)

@t.overload
def add_link(
    item_or_item_name: Item_T,
    channel_uid_or_string: t.Union[ChannelUID, str],
) -> t.Union[Item_T, None]: ...
@t.overload
def add_link(
    item_or_item_name: str,
    channel_uid_or_string: t.Union[ChannelUID, str],
) -> t.Union[GenericItem, None]: ...
@t.overload
def remove_link(
    item_or_item_name: Item_T,
    channel_uid_or_string: t.Union[ChannelUID, str],
) -> t.Union[Item_T, None]: ...
@t.overload
def remove_link(
    item_or_item_name: str,
    channel_uid_or_string: t.Union[ChannelUID, str],
) -> t.Union[GenericItem, None]: ...
@t.overload
def remove_all_links(
    item_or_item_name: Item_T
) -> t.Union[Item_T, None]: ...
@t.overload
def remove_all_links(
    item_or_item_name: str
) -> t.Union[GenericItem, None]: ...
