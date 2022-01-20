import unittest
from pathlib import Path

from linecompress import LinesFile

p = Path(__file__).parent / "data" / "cross_platform.xz"


class TestCross(unittest.TestCase):
    def test(self):
        lf = LinesFile(p)
        self.assertEqual(list(lf.read()), ['Line one', 'Line two', 'Line three'])


def _create_data():
    # тут я создаю файл в одной системе (скорее всего, POSIX), а тестировать
    # его буду в разных (POSIX, Windows)

    lf = LinesFile(p)
    lf.write('Line one')
    lf.write('Line two')
    lf.write('Line three')

if __name__ == "__main__":
    _create_data()