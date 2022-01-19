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

## LinesDir

`LinesDir` is useful if the amount of data is too large to store in one file.
It automatically creates new files when the size of the previous one gets too
big.

```python3
from pathlib import Path
from linecompress import LinesDir

storage = LinesDir(Path('/parent/dir'),
                   max_file_size=1024*1024)
storage.add('Line one')
storage.add('Line two')

for line in storage.iter_lines():
    print(line)
```

The file names are something like this:
```
000/000/000.xz
000/000/001.xz
000/000/002.xz
...
000/000/999.xz
000/001/000.xz

... and so on
```