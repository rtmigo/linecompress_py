import lzma
from pathlib import Path
from typing import List


class LinesFile:
    def __init__(self, file: Path):
        self._file = file

    def add(self, data: str):
        if '\n' in data:
            raise ValueError('Newline in the data')
        with lzma.open(self._file, "a") as lzf:
            lzf.write(data.encode())
            lzf.write(b'\n')
            lzf.flush()

    def read(self) -> List[str]:
        try:
            with lzma.open(self._file, "rb") as lzf:
                return [d.decode().rstrip('\n') for d in lzf.readlines()]
        except FileNotFoundError:
            return []

    @property
    def size(self) -> int:
        try:
            return self._file.stat().st_size
        except FileNotFoundError:
            return 0
