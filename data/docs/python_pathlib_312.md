---
doc_id: python_pathlib_312
version: Python 3.12
source_url: https://docs.python.org/3.12/library/pathlib.html
---

# pathlib — Object-oriented filesystem paths
This module offers classes representing filesystem paths with semantics appropriate for different operating systems. Path classes are divided between pure paths, which provide purely computational operations without I/O, and concrete paths, which inherit from pure paths and provide I/O operations.

# pathlib.Path.read_text
`Path.read_text(encoding=None, errors=None)` returns the contents of the file as a string. The file is opened and then closed. The optional parameters have the same meaning as in `open()`.

# pathlib.Path.read_bytes
`Path.read_bytes()` returns the binary contents of the pointed-to file as a bytes object. The file is opened and then closed.

# pathlib.Path.write_text
`Path.write_text(data, encoding=None, errors=None, newline=None)` opens the file pointed to in text mode, writes data to it, and closes the file. The number of characters written is returned.

# pathlib.Path.write_bytes
`Path.write_bytes(data)` opens the file pointed to in binary mode, writes data to it, and closes the file. The number of bytes written is returned.

# pathlib.Path.open
`Path.open(mode='r', buffering=-1, encoding=None, errors=None, newline=None)` opens the file pointed to by the path, like the built-in `open()` function.

# pathlib.Path.exists
`Path.exists()` returns `True` if the path points to an existing file or directory. `False` will be returned if the path is missing or if it is a broken symlink.

# pathlib.Path.is_file
`Path.is_file()` returns `True` if the path points to a regular file (or a symbolic link pointing to a regular file). `False` is returned if the path points to another kind of file.

# pathlib.Path.is_dir
`Path.is_dir()` returns `True` if the path points to a directory (or a symbolic link pointing to a directory). `False` is returned if the path points to another kind of file.

# pathlib.Path.glob
`Path.glob(pattern)` glob the given relative pattern in the directory represented by this path, yielding all matching files (of any kind).

# pathlib.Path.rglob
`Path.rglob(pattern)` recursively glob the given relative pattern in the directory represented by this path, yielding all matching files (of any kind).

# pathlib version notes
In Python 3.12, `Path.walk()` was added. It generates the file names in a directory tree by walking the tree top-down or bottom-up. `Path.walk(top_down=True, on_error=None, follow_symlinks=False)` yields a 3-tuple `(dirpath, dirnames, filenames)`.
In Python 3.12, the `follow_symlinks` parameter was added to `Path.is_file()` and `Path.is_dir()`. When `follow_symlinks` is `False`, symbolic links are not followed.
