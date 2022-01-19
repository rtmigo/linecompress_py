import random
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional, List

from linecompress._dir import NumberedFilePath, _split_nums, _combine_nums, \
    LinesDir
from linecompress._search_last import _num_prefix, _strings_sorted_by_num_prefix


class TestFindingFiles(unittest.TestCase):
    def test_num_prefix(self):
        self.assertEqual(_num_prefix('0'), 0)
        self.assertEqual(_num_prefix('000'), 0)
        self.assertEqual(_num_prefix('123'), 123)

        self.assertEqual(_num_prefix('12345+'), 12345)
        self.assertEqual(_num_prefix('45zzz'), 45)

        self.assertEqual(_num_prefix('abc'), None)
        self.assertEqual(_num_prefix('x123'), None)

    def test_item_with_max_num_prefix(self):
        self.assertEqual(
            _strings_sorted_by_num_prefix(['500', '502', '501'], reverse=True),
            ['502', '501', '500'])
        self.assertEqual(
            _strings_sorted_by_num_prefix(['500.xz', '502.xz', '501.xz'],
                                          reverse=True),
            ['502.xz', '501.xz', '500.xz'])
        self.assertEqual(
            _strings_sorted_by_num_prefix(['500.xz', '502.zip', '501.xz'],
                                          reverse=True),
            ['502.zip', '501.xz', '500.xz'])

    def test_item_with_max_num_prefix_no_items(self):
        self.assertEqual(
            _strings_sorted_by_num_prefix([], reverse=False),
            [])
        self.assertEqual(
            _strings_sorted_by_num_prefix(['abc', 'def'], reverse=True),
            [])


class TestNums(unittest.TestCase):
    def test_split_nums(self):
        self.assertEqual(_split_nums(123456789), [123, 456, 789])
        self.assertEqual(_split_nums(12304560789), [12, 304, 560, 789])

    def test_length(self):
        self.assertEqual(_split_nums(123, length=1), [123])
        self.assertEqual(_split_nums(123, length=2), [0, 123])
        self.assertEqual(_split_nums(123, length=3), [0, 0, 123])

        with self.assertRaises(ValueError):
            _split_nums(123456, length=1)
        self.assertEqual(_split_nums(123456, length=2), [123, 456])
        self.assertEqual(_split_nums(123456, length=3), [0, 123, 456])

    def test_combine(self):
        self.assertEqual(_combine_nums([123, 456]), 123456)
        self.assertEqual(_combine_nums([1]), 1)

    def test_split_combine_random(self):
        for _ in range(1000):
            src = random.randint(0, 9999999999999999)
            nums = _split_nums(src)
            self.assertEqual(_combine_nums(nums), src)


class TestDir(unittest.TestCase):

    def test_first(self):
        self.assertEqual(
            NumberedFilePath.first(Path("/path/to")).path,
            Path('/path/to/000/000/000'))

    def test_first_subdirs(self):
        self.assertEqual(
            NumberedFilePath.first(Path("/path/to")).path,
            Path('/path/to/000/000/000'))
        self.assertEqual(
            NumberedFilePath.first(Path("/path/to"), subdirs=5).path,
            Path('/path/to/000/000/000/000/000/000'))
        self.assertEqual(
            NumberedFilePath.first(Path("/path/to"), subdirs=0).path,
            Path('/path/to/000'))

    def test_first_with_suffix(self):
        self.assertEqual(
            NumberedFilePath.first(Path("/path/to"), suffix='.zip').path,
            Path('/path/to/000/000/000.zip'))

    def test_first_empty_path(self):
        self.assertEqual(
            NumberedFilePath.first(Path("")).path,
            Path('000/000/000'))

    def test_next_with_suffix(self):
        file = NumberedFilePath.first(Path("/path/to"), suffix='.zip')
        self.assertEqual(
            file.next.path,
            Path('/path/to/000/000/001.zip'))

    def test_next(self):
        self.assertEqual(
            NumberedFilePath.from_path(Path('/a/b/c/000/000/000.xz')).next.path,
            Path('/a/b/c/000/000/001.xz'))
        self.assertEqual(
            NumberedFilePath.from_path(Path('/a/b/c/000/000/998.xz')).next.path,
            Path('/a/b/c/000/000/999.xz'))
        self.assertEqual(
            NumberedFilePath.from_path(Path('/a/b/c/000/000/999.xz')).next.path,
            Path('/a/b/c/000/001/000.xz'))
        self.assertEqual(
            NumberedFilePath.from_path(Path('/a/b/c/000/999/999.xz')).next.path,
            Path('/a/b/c/001/000/000.xz'))

    def test_next_too_large(self):
        # no problems:
        _ = NumberedFilePath.from_path(Path('/a/b/c/999/999/998.xz')).next
        # problems:
        with self.assertRaises(ValueError):
            _ = NumberedFilePath.from_path(Path('/a/b/c/999/999/999.xz')).next

    def test_parse_path(self):
        for p in [
            Path('/path/to/123/456/789'),
            Path('/path/to/123/456/789.zip'),
            Path('/path/to/123/456/789file.xz'),
            Path('123/456/789'),
        ]:
            with self.subTest(p):
                nfp = NumberedFilePath.from_path(p)
                self.assertEqual(nfp.path, p)


class TestLastFile(unittest.TestCase):
    td: Optional[TemporaryDirectory] = None

    def setUp(self) -> None:
        self.td = TemporaryDirectory()

    def tearDown(self) -> None:
        self.td.cleanup()

    def _create_and_compare(self, files_to_create: List[str],
                            last: Optional[str]):
        root = Path(self.td.name)

        random.shuffle(files_to_create)
        for f in files_to_create:
            fullpath = (root / f)
            fullpath.parent.mkdir(parents=True, exist_ok=True)
            fullpath.touch()

        if last is None:
            self.assertIsNone(LinesDir(root)._numerically_last_file())
        else:
            self.assertEqual(
                LinesDir(root)._numerically_last_file(),
                Path(self.td.name) / last)

    def _create_and_compare_to_last(self, files_to_create: List[str],
                                    last: Optional[str] = None):
        if last is None:
            last = files_to_create[-1]
        self._create_and_compare(files_to_create=files_to_create, last=last)

    def test_last_file(self):
        for lst in [
            [
                '000/000/000.xz',
                '000/000/001.xz',
                '000/000/002.xz',
            ],
            [
                '000/000/888.xz',
                '000/000/889.xz',
                '000/002/001.xz',
            ],
            [
                '000/000/888.xz',
                '000/000/889.xz',
                '000/002/001.xz',
                '005/002/001.xz',
            ],
        ]:
            self._create_and_compare_to_last(lst)

    def test_back_from_empty_dirs(self):
        self._create_and_compare_to_last(
            [
                '000/000/888.xz',
                '000/000/889.xz',
                '000/002/001.xz',
                '005/002/001.xz',
                '006/098/',
                '006/099/',
                '026/',
                '076/099/',
            ],
            "005/002/001.xz"
        )

    def test_empty(self):
        self._create_and_compare(
            [],
            None)
        # some dirs, some files, but nothing relevant
        self._create_and_compare(
            ['000/000',
             '000/001',
             '002/001',
             '005/005/abc',
             '005/005/def',
             ],
            None)


def _rnd(n: int) -> str:
    return ''.join(random.choice('0123456789') for _ in range(n))


class TestFillDir(unittest.TestCase):
    def test_writing(self):
        with TemporaryDirectory() as tds:
            parent = Path(tds)
            ld = LinesDir(path=parent, max_file_size=150)

            def add_random_line():
                ld.add(_rnd(50))

            def expect(fn):
                self.assertEqual(ld._file_for_appending(),
                                 parent / fn)

            expect('000/000/000.xz')
            add_random_line()
            expect('000/000/000.xz')
            add_random_line()
            expect('000/000/001.xz')

    def test_reading(self):
        source = Path(__file__).parent / "data" / "dancing.txt"
        lines = source.read_text().splitlines()
        self.assertEqual(len(lines), 1130)

        with TemporaryDirectory() as tds:
            parent = Path(tds)
            ld = LinesDir(path=parent, max_file_size=1024)
            for line in lines:
                ld.add(line)

            created_files = sum(1 for _ in parent.rglob('*'))
            self.assertGreater(created_files, 50)
            self.assertLess(created_files, 500)

            lines_read = 0
            for a, b in zip(ld.iter_lines(), lines):
                lines_read += 1
                self.assertEqual(a, b)

            self.assertEqual(lines_read, 1130)
