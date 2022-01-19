import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from linecompress._file import LinesFile


class TestFile(unittest.TestCase):
    def test_cl(self):
        with TemporaryDirectory() as tds:
            file = Path(tds)/"data.xz"
            cl = LinesFile(file)
            cl.add('line one')
            cl.add('line two')

            self.assertEqual(cl.read(), ['line one', 'line two'])

            cl.add('Third line')
            self.assertEqual(cl.read(), ['line one', 'line two', 'Third line'])

    def test_read_empty(self):
        with TemporaryDirectory() as tds:
            file = Path(tds)/"data.xz"
            cl = LinesFile(file)
            self.assertEqual(cl.read(), [])

    def test_add_empty(self):
        with TemporaryDirectory() as tds:
            file = Path(tds)/"data.xz"
            cl = LinesFile(file)
            cl.add('')
            cl.add('empty')
            cl.add('')
            cl.add('')
            self.assertEqual(cl.read(), ['', 'empty', '', ''])

    def test_size(self):
        with TemporaryDirectory() as tds:
            file = Path(tds)/"data.xz"
            cl = LinesFile(file)

            for _ in range(2):
                self.assertFalse(file.exists())
                self.assertEqual(cl.size, 0)

            cl.add('Some data to be compressed')
            self.assertEqual(cl.size, 84)