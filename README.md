# [linecompress](https://github.com/rtmigo/linecompress_py#readme)

## LinesFile

`LinesFile` keeps strings in a LZMA compressed binary file.

```python3
from pathlib import Path
from linecompress import LinesFile

file = LinesFile(Path('/dir/file.xz'))
file.add('Line one')
file.add('Line two')

file.read()  # ['Line one', 'Line two']

file.add('Line three')
file.read()  # ['Line one', 'Line two', 'Line three']
```