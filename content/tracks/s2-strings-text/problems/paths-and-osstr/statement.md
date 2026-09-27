File-handling helpers that must work on any Unix path, including names that aren't valid UTF-8. Work
with `Path`, `OsStr` and `PathBuf`; converting a whole path to `&str` first gets several of these wrong.

- `ext_lower(path)`: the file name's extension, ASCII-lowercased, if it has one and it's valid UTF-8.
  Use std's definition: `".bashrc"` has none, `"a.tar.gz"` has `"gz"`, `"file."` has `""`.
- `display_name(path)`: the file name for display, with U+FFFD for bytes that aren't UTF-8; `""` when the
  path has no file name (`"/"`, `".."`). Borrow when it's valid UTF-8.
- `backup_path(path)`: the same path with `.bak` appended to the file name (`"notes.txt"` →
  `"notes.txt.bak"`), even when the name isn't UTF-8. `None` when there's no file name.
- `relative_to(paths, root)`: for each path inside `root`, compared by whole components, the rest of the
  path as `&str`, in order. Skip paths outside `root` and paths whose rest isn't UTF-8. `root` itself gives
  `""`.
