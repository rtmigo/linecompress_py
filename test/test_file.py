import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


from linecompress._file import _remove_suffix, to_compressed_path, to_rawdata_path, \
    to_dirty_path, LinesFile


class TestFile(unittest.TestCase):
    def test_cl(self):
        with TemporaryDirectory() as tds:
            file = Path(tds) / "data.txt.xz"
            cl = LinesFile(file)
            cl.append('line one')
            cl.append('line two')

            self.assertEqual(list(cl), ['line one', 'line two'])

            cl.append('Third line')
            self.assertEqual(list(cl),
                             ['line one', 'line two', 'Third line'])

    def test_read_empty(self):
        with TemporaryDirectory() as tds:
            file = Path(tds) / "data.txt.xz"
            cl = LinesFile(file)
            self.assertEqual(list(cl), [])

    def test_add_empty(self):
        with TemporaryDirectory() as tds:
            file = Path(tds) / "data.txt.xz"
            cl = LinesFile(file)
            cl.append('')
            cl.append('empty')
            cl.append('')
            cl.append('')
            self.assertEqual(list(cl), ['', 'empty', '', ''])

    def test_size(self):
        with TemporaryDirectory() as tds:
            file = Path(tds) / "data.txt.xz"
            cl = LinesFile(file)

            for _ in range(2):
                self.assertFalse(file.exists())
                self.assertEqual(cl.size, 0)

            cl.append('Some data')
            self.assertEqual(cl.size, 10)

    def test_compressed_is_smaller(self):
        with TemporaryDirectory() as tds:
            file = Path(tds) / "data.txt.xz"
            cl = LinesFile(file)

            dancing_file = (Path(__file__).parent / "data" / "dancing.txt")
            dancing_text = dancing_file.read_text()

            for line in dancing_text.splitlines():
                cl.append(line)

            with self.subTest("Originally the size is the same"):
                self.assertEqual(len(os.listdir(tds)), 1)
                self.assertEqual(len(dancing_text.encode()), 57315)
                self.assertEqual(cl.is_compressed, False)
                self.assertEqual(cl.size, 57315)

            with self.subTest("Lines are the same"):
                for a, b in zip(cl, dancing_text.splitlines()):
                    self.assertEqual(a, b)

            cl.compress()
            self.assertEqual(cl.is_compressed, True)

            with self.subTest("Original and temp files are removed"):
                self.assertEqual(len(os.listdir(tds)), 1)

            with self.subTest("Compressed file is smaller"):
                self.assertLess(cl.size, 40000)
                self.assertGreater(cl.size, 5000)

            with self.subTest("Lines are the same"):
                for a, b in zip(cl, dancing_text.splitlines()):
                    self.assertEqual(a, b)

    def test_suffix(self):
        self.assertEqual(
            _remove_suffix('my.file.name.txt'),
            'my.file.name')
        self.assertEqual(
            _remove_suffix('my.file.name.txt.xz'),
            'my.file.name')
        self.assertEqual(
            _remove_suffix('my.file.name.txt.xz.tmp'),
            'my.file.name')
        with self.assertRaises(ValueError):
            _remove_suffix('my.file.name.jpg')

    def test_name(self):

        source_names = [Path('/path/to/my.file.name.txt'),
                        Path('/path/to/my.file.name.txt.xz'),
                        Path('/path/to/my.file.name.txt.xz.tmp')]
        for src in source_names:
            self.assertEqual(
                to_compressed_path(src),
                Path('/path/to/my.file.name.txt.xz'))
            self.assertEqual(
                to_dirty_path(src),
                Path('/path/to/my.file.name.txt.xz.tmp'))
            self.assertEqual(
                to_rawdata_path(src),
                Path('/path/to/my.file.name.txt'))
