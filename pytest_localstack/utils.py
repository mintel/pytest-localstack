"""Misc utilities."""
import os
import sys
import types

import six

if sys.version_info >= (3, 3):
    import contextlib
    from unittest import mock
else:
    import contextlib2 as contextlib
    import mock  # noqa


def check_proxy_env_vars():
    """Raise warnings about improperly-set proxy environment variables."""
    proxy_settings = six.moves.urllib.request.getproxies()
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
def nested(*mgrs):
    """Combine multiple context managers."""
    with contextlib.ExitStack() as stack:
        outputs = [stack.enter_context(cm) for cm in mgrs]
        yield outputs


def unbind(func):
    """Get Function from Method (if not already Function)."""
    if isinstance(func, types.MethodType):
        func = six.get_method_function(func)
    return func


def remove_newline(string, n=1):
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
