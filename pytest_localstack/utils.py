"""Misc utilities."""
import os
import string
import types
from typing import Tuple

from pytest_localstack import exceptions


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


def get_version_tuple(version: str) -> Tuple[int]:
    """
    Return a tuple of version numbers (e.g. (1, 2, 3)) from the version
    string (e.g. '1.2.3').
    """
    if version[0] == "v":
        version = version[1:]
    parts = version.split(".")
    return tuple(int(p) for p in parts)


def check_supported_localstack_image(image: str):
    """
    Checks a Localstack Docker image ref to see if the version
    tag is one that pytest-localstack supports.
    """
    image_parts = image.split(":", 1)
    if len(image_parts) < 2:
        return  # No tag, so latest image.
    tag = image_parts[1]
    if tag[0] != "v":
        # Not a version tag. Assume it's ok.
        return
    version = get_version_tuple(tag)
    if version >= (0, 11, 6):
        # This is a
        return
    raise exceptions.UnsupportedLocalstackVersionError(image)


def generate_random_string(n: int = 6) -> str:
    """Generate a random string of ascii chars, n chars long."""
    valid_chars = set(string.ascii_letters)
    chars = []
    while len(chars) < 6:
        new_chars = [chr(c) for c in os.urandom(6 - len(chars))]
        chars += [c for c in new_chars if c in valid_chars]
    return "".join(chars)
