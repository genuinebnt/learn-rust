**Where this fits.** A new db file starts with room for `DEFAULT_DB_IO_SIZE` pages, and the disk manager can say how big the file is.

## The task

In `src/storage/disk/disk_manager.rs`:
- in `DiskManager::new`, after opening, make the db file `file_size_for(DEFAULT_DB_IO_SIZE)` bytes long;
- `get_db_file_size()` returns the db file's length in bytes right now. It may `expect` that the file exists.

## Tests

- A new db file is `17 * 8192` bytes, and `get_db_file_size()` agrees with `std::fs::metadata`.
- The new room reads as zeros; opening the same file again keeps the size and any bytes already inside it.

## Syntax and methods

```rust
file.set_len(n_bytes)?;                           // io::Result<()>: the file is now exactly n bytes; new bytes are zero
let len: u64 = std::fs::metadata(&path)?.len();   // a file's size, by path
opt_or_result.expect("message")                   // unwrap, with your message in the panic
```

## Notes

Operating systems store a file that was extended this way **sparsely**: the zero bytes take no disk blocks until something is written there (compare `ls -l` and `ls -ls`). Extending is nearly free; that's why BusTub does it up front.

## In BusTub

```cpp
std::filesystem::resize_file(db_file, (page_capacity_ + 1) * BUSTUB_PAGE_SIZE);
...
auto DiskManager::GetFileSize(const std::string &file_name) -> int {
  struct stat stat_buf;
  int rc = stat(file_name.c_str(), &stat_buf);
  return rc == 0 ? static_cast<int>(stat_buf.st_size) : -1;   // an int: files over 2 GB overflow; -1 for "error"
}
```

The port returns `u64` and treats a vanished db file as a bug, instead of returning `-1` for callers to forget to check.

## The C/C++ way
| C / C++ | Rust |
|---|---|
| `ftruncate(fd, len)`; `std::filesystem::resize_file(path, len)` | `file.set_len(len)` |
| `posix_fallocate(fd, 0, len)` (really reserves blocks; not sparse) | no std equivalent (use `rustix::fs::fallocate`) |
| `struct stat st; stat(path, &st); st.st_size`, `fstat(fd, &st)` | `fs::metadata(path)?.len()`, `file.metadata()?.len()` |
| BusTub's `GetFileSize` returns `int` (-1 on error) | return `u64`; errors are `Result`, never an in-band `-1` |

**Pitfall in the C++:** `static_cast<int>(st.st_size)` silently truncates files over 2 GiB, and `-1` is a legal-looking size. Both are impossible here.

## Learn more
- [`File::set_len`](https://doc.rust-lang.org/std/fs/struct.File.html#method.set_len) · [`fs::metadata`](https://doc.rust-lang.org/std/fs/fn.metadata.html)
