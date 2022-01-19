import lzma
from pathlib import Path
from typing import List, Iterable


class LinesFile:
    def __init__(self, file: Path, separator = '\n'):
        self._file = file
        self._separator = separator

    def write(self, data: str):
        if self._separator in data:
            raise ValueError('Newline in the data')
        with lzma.open(self._file, "at", encoding="utf-8") as lzf:
            lzf.write(data)
            lzf.write(self._separator)
            lzf.flush()

    def read(self) -> Iterable[str]:
        try:
            with lzma.open(self._file, "rt", encoding="utf-8", newline=self._separator) as lzf:
                for line in lzf.readlines():
                    assert isinstance(line, str)
                    line = line.rstrip(self._separator)
                    yield line

        except FileNotFoundError:
            return []

    @property
    def size(self) -> int:
        try:
            return self._file.stat().st_size
        except FileNotFoundError:
            return 0
