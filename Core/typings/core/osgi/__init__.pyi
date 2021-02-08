__all__ = [
    "REGISTERED_SERVICES",
    "get_service",
    "find_services",
    "register_service",
    "unregister_service",
]

import typing as t

from java.lang import Class, String

from org.osgi.framework import BundleContext, ServiceRegistration

_Service = t.TypeVar("_Service")

BUNDLE_CONTEXT: BundleContext = ...
REGISTERED_SERVICES: t.Dict[str, t.Tuple[_Service, ServiceRegistration[_Service]]] = ...

def get_service(class_or_name: t.Union[t.Type[Class], str]) -> t.Any: ...
def find_services(
    class_name: str, service_filter: t.Union[str, None]
) -> t.Union[t.List[t.Any], None]: ...
def register_service(
    service: _Service,
    interface_names: t.List[t.Union[String, str]],
    properties: t.Optional[t.Dict[t.Union[String, str], t.Any]],
) -> ServiceRegistration[_Service]: ...
def unregister_service(
    service: _Service,
) -> None: ...
