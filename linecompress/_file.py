import lzma
import os
import shutil
from pathlib import Path
from typing import Iterable, Union, BinaryIO

_COMPRESSED_SUFFIX = '.txt.xz'
_DECOMPRESSED_SUFFIX = '.txt'
_DIRTY_SUFFIX = '.txt.xz.tmp'


def _remove_suffix(basename: str) -> str:
    for suf in [_COMPRESSED_SUFFIX, _DECOMPRESSED_SUFFIX, _DIRTY_SUFFIX]:
        if basename.endswith(suf):
            return basename[:-len(suf)]
    raise ValueError


def to_compressed_path(file: Path) -> Path:
    return file.parent / (_remove_suffix(file.name) + _COMPRESSED_SUFFIX)


def to_dirty_path(file: Path) -> Path:
    return file.parent / (_remove_suffix(file.name) + _DIRTY_SUFFIX)


def to_rawdata_path(file: Path) -> Path:
    return file.parent / (_remove_suffix(file.name) + _DECOMPRESSED_SUFFIX)


def is_compressed_path(file: Path) -> bool:
    return file.name.endswith(_COMPRESSED_SUFFIX)


def is_dirty_path(file: Path) -> bool:
    return file.name.endswith(_DIRTY_SUFFIX)


def is_rawdata_path(file: Path) -> bool:
    return file.name.endswith(_DECOMPRESSED_SUFFIX)


class LinesFile(Iterable[str]):
    def __init__(self, file: Path):

        dirty = to_dirty_path(file)
        if dirty.exists():
            os.remove(dirty)

        compressed = to_compressed_path(file)
        raw = to_rawdata_path(file)

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

        temp_name = to_dirty_path(self._file)
        compressed_name = to_compressed_path(self._file)
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

    def iter_str_lines(self) -> Iterable[str]:
        f = None
        try:
            if self.is_compressed:
                f = lzma.open(self._file, "rt", encoding="utf-8", newline='\n')
            else:
                f = self._file.open("rt", encoding="utf-8", newline='\n')

            for line in f.readlines():
                line = line[:-1]
                yield line

        except FileNotFoundError:
            pass
        finally:
            if f is not None:
                f.close()

    def iter_byte_lines(self) -> Iterable[bytes]:
        f: Union[BinaryIO, lzma.LZMAFile, None] = None
        try:
            if self.is_compressed:
                f = lzma.open(self._file, "rb")
            else:
                f = self._file.open("rb")

            for line in f.readlines():
                line = line[:-1]
                yield line

        except FileNotFoundError:
            pass
        finally:
            if f is not None:
                f.close()

    def __iter__(self):
        return self.iter_str_lines()

    @property
    def size(self) -> int:
        try:
            return self._file.stat().st_size
        except FileNotFoundError:
            return 0
