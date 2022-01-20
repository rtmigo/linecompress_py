import lzma
from pathlib import Path
from typing import List, Iterable


class LinesFile(Iterable[str]):
    def __init__(self, file: Path):
        self._file = file

    def append(self, data: str):
        if '\n' in data:
            raise ValueError('Newline in the data')
        with lzma.open(self._file, "at", encoding="utf-8", newline='\n') as lzf:
            lzf.write(data)
            lzf.write('\n')
            lzf.flush()

    def __iter__(self):
        try:
            with lzma.open(self._file, "rt",
                           encoding="utf-8", newline='\n') as lzf:
                for line in lzf.readlines():
                    assert isinstance(line, str)
                    line = line[:-1]
                    yield line

        except FileNotFoundError:
            return []

    @property
    def size(self) -> int:
        try:
            return self._file.stat().st_size
        except FileNotFoundError:
            return 0
