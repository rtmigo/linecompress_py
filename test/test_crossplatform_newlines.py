import unittest
from pathlib import Path

from linecompress._file import LinesFile

p = Path(__file__).parent / "data" / "cross_platform.txt.gz"


class TestCross(unittest.TestCase):
    def test(self):
        lf = LinesFile(p)
        self.assertEqual(list(lf), ['Line one', 'Line two', 'Line three'])


def _create_data():
    # тут я создаю файл в одной системе (скорее всего, POSIX), а тестировать
    # его буду в разных (POSIX, Windows)

    lf = LinesFile(p)
    lf.append('Line one')
    lf.append('Line two')
    lf.append('Line three')
    lf.compress()

if __name__ == "__main__":
    _create_data()