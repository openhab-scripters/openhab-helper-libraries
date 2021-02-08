import typing as t
import logging

LOG_PREFIX: str

_RT = t.TypeVar("_RT")

class Slf4jLogger(logging.Logger):
    def trace(self, msg: t.Any, *args: t.Any, **kwargs: t.Any) -> None: ...

def getLogger(name: t.Optional[str], prefix: t.Optional[str] = ...) -> Slf4jLogger: ...
def log_traceback(function: t.Callable[..., _RT]) -> t.Callable[..., _RT]: ...
