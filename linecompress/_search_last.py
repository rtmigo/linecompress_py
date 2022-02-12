"""Функции, помогающие в дереве каталогов найти файл вроде 123/456/789.zip,
у которого вот это число 123456789 максимально.

Мы стремимся НЕ обходить рекурсивно все дерево каталогов. Мы просто берем
последний подкаталог из '123/', потом последний файл из '123/456/'.

Возможен подвох: например, у нас есть пустой каталог '999/' и пустой '999/888'.
Их нужно проигнорировать и добраться до '123/456/789.zip' кратчайшим путем.

Среди файлов и каталогов нас интересуют только те, имена которых начинаются
с чисел. Например, '555', '555suffix', '555.zip'.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional, List, Iterable


def _num_prefix(text: str) -> Optional[int]:
    s = _num_prefix_str(text)
    return int(s) if s is not None else None


def _num_prefix_str(text: str) -> Optional[str]:
    m = re.search(r'^\d+', text)
    if m is None:
        return None
    return m.group(0)


class NoItems(ValueError):
    pass


def _strings_sorted_by_num_prefix(names_same_dir: List[str],
                                  reverse: bool) -> List[str]:
    lst = [(_num_prefix(s), s) for s in names_same_dir]
    lst = [item for item in lst if item[0] is not None]
    lst.sort(reverse=reverse)
    return [name for (_, name) in lst]


def _paths_sorted_by_num_prefix(parent: Path, reverse: bool) \
        -> Iterable[Path]:
    for name in _strings_sorted_by_num_prefix(
            [p.name for p in parent.glob('*')],
            reverse=reverse):
        yield parent / name


def _recurse_paths(parent: Path, reverse: bool, go_deeper: int) \
        -> Iterable[Path]:
    """Обходим дерево каталогов.

    Все результаты будут отсортированы по значениям числовых префиксов:
        100a/200b/998c
        100a/200b/999c
        100a/201b/000c

    Если числового префикса нет - путь (файл или каталог) игнорируется.

    Пустые каталоги игнорируются.

    Короткие пути, вроде '100a/200b', если мы ищем путь из трех частей -
    игнорируются.
    """
    if go_deeper == 0:
        for result in _paths_sorted_by_num_prefix(parent, reverse=reverse):
            yield result
    # todo else?
    for sub in _paths_sorted_by_num_prefix(parent, reverse=reverse):
        for result in _recurse_paths(
                parent=sub, go_deeper=go_deeper - 1, reverse=reverse):
            yield result
