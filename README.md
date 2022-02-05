# [linecompress](https://github.com/rtmigo/linecompress_py#readme)

Library for storing text strings in compressed files.

It uses **.xz** compression format, so the data can be decompressed by any
compression utility with .xz support.

Lines can be appended to existing archives one by one.

## LinesDir

`LinesDir` saves data to multiple files, making sure the files don't get too
big.

The files are filled sequentially: first we write only to `000.txt.xz`, then 
only to `001.txt.xz`, and so on.


```python3
from pathlib import Path
from linecompress import LinesDir

lines_dir = LinesDir(Path('/parent/dir'),
                     max_file_size=1000000)
lines_dir.append('Line one')
lines_dir.append('Line two')

# reading from oldest to newest
for line in lines_dir:
    print(line)

# reading from newest to oldest
for line in reversed(lines_dir):
    print(line)
```

### Directory structure

```
000/000/000.txt.xz 
000/000/001.txt.xz 
000/000/002.txt.xz 
...
000/000/999.txt.xz 
000/001/000.txt.xz
...
000/001/233.txt.xz 
000/001/234.txt 
```

The last file usually contains raw text, not yet compressed.

### Limitations

The default maximum file size is 1 million bytes (decimal megabyte).

This is the size of text data *before* compression.

The directory will hold up to a billion of these files. Thus, the maximum total
storage size is one decimal petabyte.

By changing the value of the `subdirs` argument, we change the maximum number of
files: an increase in `subdirs` by one means an increase in the number of 
files by a thousand times.

With the default file size 1MB we get the following limits:


| subdirs     | file path            | max sum size |
|-------------|----------------------|--------------|
| `subdirs=0` | `000.xz`             | gigabyte     |
| `subdirs=1` | `000/000.xz`         | terabyte     |
| `subdirs=2` | `000/000/000.xz`     | petabyte     |
| `subdirs=3` | `000/000/000/000.xz` | exabyte      |

These are the data sizes before compression. The actual size of the files on 
the disk will most likely be smaller.

Adjusting the limits:

```python3
from pathlib import Path
from linecompress import LinesDir

gb = LinesDir(Path('/max/gigabyte'),
              subdirs=1)

# subdirs=2 is the default value
pb = LinesDir(Path('/max/petabyte'))

eb = LinesDir(Path('/max/exabyte'),
              subdirs=3)
```

The file size can also be adjusted.

```python3
from pathlib import Path
from linecompress import LinesDir

# the default buffer size is 1 MB
pb = LinesDir(Path('/max/petabyte'))

# set file size to 5 MB
pb5 = LinesDir(Path('/max/5_petabytes'),
               buffer_size=5000000)
```

* With larger files, we get better compression and less load on the file system.
* With smaller files, we're much more efficient at iterating through lines in 
  reverse order.