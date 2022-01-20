from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional, Iterable

from linecompress import LinesFile
from linecompress._search_last import _recurse_paths, _num_prefix_str


def _split_nums(x: int, length: Optional[int] = None) -> List[int]:
    result: List[int] = []
    while True:
        result.append(x % 1000)
        x = x // 1000
        if x == 0:
            break

    if length is not None:
        if len(result) > length:
            raise ValueError
        while len(result) < length:
            result.append(0)
    result.reverse()
    return result


def _combine_nums(nums: List[int]) -> int:
    return sum((1000 ** power) * num
               for power, num in enumerate(reversed(nums)))


class NumberedFilePath:
    def __init__(self, root: Path, nums: List[int], suffix: str):
        self.root = root
        for n in nums:
            if not 0 <= n <= 999:
                raise ValueError(n)
        self.subs = nums
        self.suffix = suffix

    @property
    def path(self):
        result = self.root
        for s in self.subs:
            result = result / f'{s:03d}'
        if self.suffix:
            result = result.parent / (result.name + self.suffix)
        return result

    @staticmethod
    def first(root: Path, suffix: str = '',
              subdirs: int = 2) -> NumberedFilePath:
        return NumberedFilePath(root=root, nums=[0] * (subdirs + 1),
                                suffix=suffix)

    @property
    def next(self):
        return NumberedFilePath(
            root=self.root,
            nums=_split_nums(_combine_nums(self.subs) + 1,
                             length=len(self.subs)),
            suffix=self.suffix)

    @staticmethod
    def from_path(file: Path, subdirs: int = 2) -> NumberedFilePath:
        filenum = _num_prefix_str(file.name)
        if filenum is None:
            raise ValueError(file)
        suffix = file.name[len(filenum):]
        nums = [int(filenum)]

        p = file
        for _ in range(subdirs):
            p = p.parent
            nums.append(int(p.name))
        nums.reverse()

        root = p.parent

        result = NumberedFilePath(root=root, nums=nums, suffix=suffix)
        assert result.path == file, f"{result.path}, {file}"
        return result


class LinesDir:
    def __init__(self,
                 path: Path,
                 subdirs: int = 2,
                 max_file_size: int = 30 * 1024 * 1024):
        self._path = path
        self._subdirs = subdirs
        self.max_file_size = max_file_size


    def _recurse_files(self, reverse: bool) -> Iterable[Path]:
        return _recurse_paths(parent=self._path,
                              go_deeper=self._subdirs,
                              reverse=reverse)

    def _numerically_last_file(self) -> Optional[Path]:
        for first in self._recurse_files(reverse=True):
            return first
        return None

    def _file_for_appending(self) -> Path:
        """Если файл с максимальным числовым именем не особо большой,
        возвращаем его. Иначе возвращаем новое имя файла.
        """
        last = self._numerically_last_file()
        if last is None:
            # file does not exist
            return NumberedFilePath(self._path, [0] * (self._subdirs + 1),
                                    '.xz').path
        if last.stat().st_size >= self.max_file_size:
            # file is too large
            return NumberedFilePath.from_path(last, subdirs=self._subdirs) \
                .next.path
        # file is ok
        return last

    def write(self, text: str):
        path = self._file_for_appending()
        path.parent.mkdir(parents=True, exist_ok=True)
        LinesFile(path).write(text)

    def read(self) -> Iterable[str]:
        for file in self._recurse_files(reverse=False):
            lf = LinesFile(file)
            for line in lf.read():
                yield line
