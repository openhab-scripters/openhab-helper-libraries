import typing as t

try:
    from org.openhab.core.items import GenericItem
except:
    from org.eclipse.smarthome.core.items import GenericItem

Item_T = t.TypeVar("Item_T", bound=GenericItem)

@t.overload
def add_item(
    item_or_item_name: str,
    item_type: t.Optional[str] = ...,
    category: t.Optional[str] = ...,
    groups: t.Optional[t.List[str]] = ...,
    label: t.Optional[str] = ...,
    tags: t.List = ...,
    gi_base_type: t.Optional[str] = ...,
    group_function: t.Optional[str] = ...,
) -> t.Union[GenericItem, None]: ...
@t.overload
def add_item(
    item_or_item_name: Item_T,
    item_type: t.Optional[str] = ...,
    category: t.Optional[str] = ...,
    groups: t.Optional[t.List[str]] = ...,
    label: t.Optional[str] = ...,
    tags: t.List = ...,
    gi_base_type: t.Optional[str] = ...,
    group_function: t.Optional[str] = ...,
) -> t.Union[Item_T, None]: ...
@t.overload
def remove_item(item_or_item_name: str) -> t.Union[GenericItem, None]: ...
@t.overload
def remove_item(item_or_item_name: Item_T) -> t.Union[Item_T, None]: ...
