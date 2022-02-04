import lzma
import os
import shutil
from pathlib import Path
from typing import Iterable

_COMPRESSED_SUFFIX = '.txt.xz'
_DECOMPRESSED_SUFFIX = '.txt'
_DIRTY_SUFFIX = '.txt.xz.tmp'


def _remove_suffix(basename: str) -> str:
    for suf in [_COMPRESSED_SUFFIX, _DECOMPRESSED_SUFFIX, _DIRTY_SUFFIX]:
        if basename.endswith(suf):
            return basename[:-len(suf)]
    raise ValueError


def _compressed(file: Path) -> Path:
    return file.parent / (_remove_suffix(file.name) + _COMPRESSED_SUFFIX)


def _dirty(file: Path) -> Path:
    return file.parent / (_remove_suffix(file.name) + _DIRTY_SUFFIX)


def _decompressed(file: Path) -> Path:
    return file.parent / (_remove_suffix(file.name) + _DECOMPRESSED_SUFFIX)


def is_compressed_name(file: Path) -> bool:
    return file.name.endswith(_COMPRESSED_SUFFIX)


def is_dirty_name(file: Path) -> bool:
    return file.name.endswith(_DIRTY_SUFFIX)


def is_rawtext_name(file: Path) -> bool:
    return file.name.endswith(_DECOMPRESSED_SUFFIX)


class LinesFile(Iterable[str]):
    def __init__(self, file: Path):

        dirty = _dirty(file)
        if dirty.exists():
            os.remove(dirty)

        compressed = _compressed(file)
        raw = _decompressed(file)

        if compressed.exists():
            self._file = compressed
            assert self.is_compressed
            if raw.exists():
                os.remove(raw)

        else:
            self._file = raw
            assert not self.is_compressed

    @property
    def is_compressed(self) -> bool:
        return self._file.name.endswith(_COMPRESSED_SUFFIX)

    def compress(self):
        if self.is_compressed:
            # todo test
            raise Exception("Cannot compress already compressed")

        temp_name = _dirty(self._file)
        compressed_name = _compressed(self._file)
        with lzma.open(temp_name, 'wb') as lzma_out:
            with self._file.open('rb') as text_in:
                shutil.copyfileobj(text_in, lzma_out)
        os.rename(temp_name, compressed_name)
        os.remove(self._file)
        self._file = compressed_name

    def append(self, data: str):
        if self.is_compressed:
            raise Exception("Cannot add to compressed file")
        if '\n' in data:
            raise ValueError('Newline in the data')
        with self._file.open("at", newline='\n') as outfile:
            outfile.write(data)
            outfile.write('\n')
            outfile.flush()

    def __iter__(self):
        f = None
        try:
            if self.is_compressed:
                f = lzma.open(self._file, "rt", encoding="utf-8", newline='\n')
            else:
                f = self._file.open("rt", encoding="utf-8", newline='\n')

            for line in f.readlines():
                assert isinstance(line, str)
                line = line[:-1]
                yield line

        except FileNotFoundError:
            return []
        finally:
            if f is not None:
                f.close()

    @property
    def size(self) -> int:
        try:
            return self._file.stat().st_size
        except FileNotFoundError:
            return 0
