"""Misc utilities."""
import contextlib
import os
import types
import urllib.request
from typing import Any, ContextManager, Iterator, List, Sequence, Tuple
from unittest import mock


def check_proxy_env_vars() -> None:
    """Raise warnings about improperly-set proxy environment variables."""
    proxy_settings = urllib.request.getproxies()
    if "http" not in proxy_settings and "https" not in proxy_settings:
        return
    for var in ["http_proxy", "https_proxy", "no_proxy"]:
        try:
            if os.environ[var.lower()] != os.environ[var.upper()]:
                raise UserWarning(
                    "Your {0} and {1} environment "
                    "variables are set to different values.".format(
                        var.lower(), var.upper()
                    )
                )
        except KeyError:
            pass
    if "no" not in proxy_settings:
        raise UserWarning(
            "You have proxy settings, but no_proxy isn't set. "
            "If you try to connect to localhost (i.e. like pytest-localstack does) "
            "it's going to try to go through the proxy and fail. "
            "Set the no_proxy environment variable to something like "
            "'localhost,127.0.0.1' (and maybe add your local network as well? ;D )"
        )
    if "127.0.0.1" not in proxy_settings["no"]:
        raise UserWarning(
            "You have proxy settings (including no_proxy) set, "
            "but no_proxy doens't contain '127.0.0.1'. "
            "This is needed for Localstack. "
            "Please set the no_proxy environment variable to something like "
            "'localhost,127.0.0.1' (and maybe add your local network as well? ;D )"
        )


@contextlib.contextmanager
def nested(*mgrs: ContextManager[Any]) -> Iterator[List[ContextManager[Any]]]:
    """Combine multiple context managers."""
    with contextlib.ExitStack() as stack:
        outputs: List[ContextManager[Any]] = [stack.enter_context(cm) for cm in mgrs]
        yield outputs


def unbind(func):
    """Get Function from Method (if not already Function)."""
    if isinstance(func, types.MethodType):
        func = func.__func__
    return func


def remove_newline(string: str, n: int = 1) -> str:
    """Remove up to `n` trailing newlines from `string`."""
    # Regex returns some weird results when dealing with only newlines,
    # so we do this manually.
    # >>> import re
    # >>> re.sub(r'(?:\r\n|\n\r|\n|\r){,1}$', '', '\n\n', 1)
    # ''
    for _ in range(n):
        if string.endswith("\r\n") or string.endswith("\n\r"):
            string = string[:-2]
        elif string.endswith("\n") or string.endswith("\r"):
            string = string[:-1]
        else:
            break
    return string


def get_version_tuple(version: str) -> Tuple[int, ...]:
    """
    Return a tuple of version numbers (e.g. (1, 2, 3)) from the version
    string (e.g. '1.2.3').
    """
    if version[0] == "v":
        version = version[1:]
    parts = version.split(".")
    return tuple(int(p) for p in parts)
