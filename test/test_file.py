import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from linecompress import LinesFile


class TestFile(unittest.TestCase):
    def test_cl(self):
        with TemporaryDirectory() as tds:
            file = Path(tds) / "data.xz"
            cl = LinesFile(file)
            cl.append('line one')
            cl.append('line two')

            self.assertEqual(list(cl), ['line one', 'line two'])

            cl.append('Third line')
            self.assertEqual(list(cl),
                             ['line one', 'line two', 'Third line'])

    def test_read_empty(self):
        with TemporaryDirectory() as tds:
            file = Path(tds) / "data.xz"
            cl = LinesFile(file)
            self.assertEqual(list(cl), [])

    def test_add_empty(self):
        with TemporaryDirectory() as tds:
            file = Path(tds) / "data.xz"
            cl = LinesFile(file)
            cl.append('')
            cl.append('empty')
            cl.append('')
            cl.append('')
            self.assertEqual(list(cl), ['', 'empty', '', ''])

    def test_size(self):
        with TemporaryDirectory() as tds:
            file = Path(tds) / "data.xz"
            cl = LinesFile(file)

            for _ in range(2):
                self.assertFalse(file.exists())
                self.assertEqual(cl.size, 0)

            cl.append('Some data to be compressed')
            self.assertEqual(cl.size, 84)

    # def test_other_separator(self):
    #     with TemporaryDirectory() as tds:
    #         file = Path(tds) / "data.xz"
    #         cl = LinesFile(file, separator='\r\n')
    #         cl.write('line one\nline two')
    #         cl.write('line three')
    #         with self.assertRaises(ValueError):
    #             cl.write('bad\r\nbad')
    #         self.assertEqual(list(cl.read()),
    #                          ['line one\nline two', 'line three'])
