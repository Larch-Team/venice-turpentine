from json import load
import os.path as osp
from typing import Iterator

def get_plugin_path(file: str, additional: str = '') -> str:
    """
    Zwraca ścieżkę absolutną do pliku wewnątrz pluginu.

    :param file: wartość zmiennej __file__ w __init__.py
    :type file: str
    :param additional: ścieżka do pliku z perspektywy folderu pluginu, defaults to None
    :type additional: str, optional
    :return: cała ścieżka
    :rtype: str
    """
    return osp.dirname(file) + bool(additional)*'/' + additional

def setup_iter(filename: str) -> Iterator[tuple[str, str]]:
    with open(filename) as f:
        setup = load(f)
    yield from setup.items()