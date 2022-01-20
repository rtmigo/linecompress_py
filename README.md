# [linecompress](https://github.com/rtmigo/linecompress_py#readme)

Library for storing multiple text strings in compressed files.

Data can be decompressed not only with this library, but also with any archive
utility that supports the XZ format.

Lines do not need to be added all at once. You can add one at a time to the 
end of an existing file or storage dir.

## LinesFile

`LinesFile` keeps strings in a LZMA compressed binary file.

```python3
from pathlib import Path
from linecompress import LinesFile

file = LinesFile(Path('/dir/file.xz'))
file.write('Line one')
file.write('Line two')

file.read()  # ['Line one', 'Line two']

file.write('Line three')
file.read()  # ['Line one', 'Line two', 'Line three']
```

## LinesDir

`LinesDir` is useful if the amount of data is too large to store in one file. It
automatically creates new files when the size of the previous one gets too big.

```python3
from pathlib import Path
from linecompress import LinesDir

storage = LinesDir(Path('/parent/dir'),
                   max_file_size=1024 * 1024)
storage.write('Line one')
storage.write('Line two')

for line in storage.read():
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