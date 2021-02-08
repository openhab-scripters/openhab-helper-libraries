__all__ = ["rule", "addRule"]

import typing as t

from org.openhab.core.automation import Rule
from org.openhab.core.automation.module.script.rulesupport.shared.simple import (
    SimpleRule,
)
from org.openhab.core.events import Event

_ReturnType = t.TypeVar("_ReturnType")
_Class = t.TypeVar("_Class")

def rule(
    name: t.Optional[str] = ...,
    description: t.Optional[str] = ...,
    tags: t.Optional[t.List[str]] = ...,
) -> t.Callable[
    [t.Union[t.Callable[[Event], _ReturnType], _Class]], t.Union[_ReturnType, _Class]
]: ...
def addRule(new_rule: SimpleRule) -> Rule: ...
