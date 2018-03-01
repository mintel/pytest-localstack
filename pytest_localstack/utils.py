"""Misc utilities."""
import os

import six


def check_proxy_env_vars():
    """Raise warnings about improperly-set proxy environment variables."""
    proxy_settings = six.moves.urllib.request.getproxies()
    if 'http' not in proxy_settings and 'https' not in proxy_settings:
        return
    for var in ['http_proxy', 'https_proxy', 'no_proxy']:
        try:
            if os.environ[var.lower()] != os.environ[var.upper()]:
                raise UserWarning(
                    "Your {0} and {1} environment "
                    "variables are set to different values.".format(
                        var.lower(),
                        var.upper(),
                    )
                )
        except KeyError:
            pass
    if 'no' not in proxy_settings:
        raise UserWarning(
            "You have proxy settings, but no_proxy isn't set. "
            "If you try to connect to localhost (i.e. like pytest-localstack does) "
            "it's going to try to go through the proxy and fail. "
            "Set the no_proxy environment variable to something like "
            "'localhost,127.0.0.1' (and maybe add your local network as well? ;D )"
        )
    if '127.0.0.1' not in proxy_settings['no']:
        raise UserWarning(
            "You have proxy settings (including no_proxy) set, "
            "but no_proxy doens't contain '127.0.0.1'. "
            "This is needed for Localstack. "
            "Please set the no_proxy environment variable to something like "
            "'localhost,127.0.0.1' (and maybe add your local network as well? ;D )"
        )
