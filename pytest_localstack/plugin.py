"""Plugins manager.

.. seealso:: :mod:`~pytest_localstack.hookspecs`

"""
import importlib

import pluggy

import pytest_localstack.hookspecs


manager = pluggy.PluginManager("pytest-localstack")
manager.add_hookspecs(pytest_localstack.hookspecs)


def register_plugin_module(module_path, required=True):
    """Register hooks in a module with the PluginManager by Python path.

    Args:
        module_path (str): A Python dotted import path.
        required (bool, optional): If False, ignore ImportError.
            Default: True.

    Returns:
        The imported module.

    Raises:
        ImportError: If `required` is True and the module cannot be imported.

    """
    try:
        module = importlib.import_module(module_path)
    except ImportError:
        if required:
            raise
    else:
        manager.register(module)
        return module
