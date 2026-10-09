---
title: Durability: when a write is really on disk
summary: What write, flush and fsync each promise, why a crash can leave a half-written page, and the three tools a storage engine uses: ordering (log before data), atomic replace (write a temp file, sync, rename) and checksums.
minutes: 9
---
A database promises that a committed change survives a crash. `file.write_all(bytes)` does not give that: it hands bytes to the **operating system's page cache**, which writes them to the device later. If the machine loses power in between, the bytes are gone, even though `write` returned `Ok`.

| call | what it guarantees |
|---|---|
| `File::write_all` | the OS has the bytes (other processes see them); not necessarily on disk |
| `BufWriter::flush` | the bytes left *your* buffer for the OS; nothing about the disk |
| `File::flush` | nothing: a `File` has no user-space buffer, so it is a no-op |
| `File::sync_data` | the file's *contents* are on stable storage (like `fdatasync`) |
| `File::sync_all` | contents **and metadata** (size, timestamps) are on stable storage (like `fsync`; on macOS Rust asks for `F_FULLFSYNC`, which also flushes the drive's own cache) |
| `fsync` of the **directory** | the directory entry (a newly created or renamed file) is durable |

`fsync` is slow (milliseconds on a disk, hundreds of microseconds on an SSD), which is why databases batch many commits behind one sync (*group commit*).

## Torn writes and what to do about them

A 4 KiB page may be written as eight 512-byte sectors; a crash in the middle leaves a **torn page**: part new, part old. Three defences, used together:

1. **Order the writes.** Write the change to a **log** first, sync the log, then update the data pages whenever convenient. After a crash, replay the log (recovery). This is the write-ahead rule that BusTub's buffer pool flush ordering follows (see the *eviction and write-back ordering* article).
2. **Replace atomically.** To change a small file (a manifest, a config), write the new version to a temporary file in the same directory, `sync_all` it, then `rename` it over the old one (rename is atomic on POSIX file systems), then `fsync` the directory. A reader sees the old file or the new one, never a mixture.
3. **Checksum pages.** Store a checksum (CRC32 or a 64-bit hash) with each page; on read, a mismatch means the page was torn or corrupted. Recovery then repairs it from the log or a backup.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `fsync(fd)`, `fdatasync(fd)` | `file.sync_all()`, `file.sync_data()` |
| `std::ofstream::flush()` (user-space buffer to the OS) | `BufWriter::flush()`; a plain `File` has no buffer |
| `rename(2)` | `std::fs::rename` |
| `O_DIRECT`, `O_DSYNC` flags | `OpenOptionsExt::custom_flags` on Unix |

**Port rule:** every place C++ calls `fsync` is `sync_all`/`sync_data`; forgetting the directory sync after a create or rename is the same bug in both languages.

## In real code

### Using it: atomic replace and a checksum

```rust test
use std::fs::{self, File};
use std::io::Write;
use std::path::Path;

/// Replaces `path` with `data` so that a crash leaves the old file or the new one.
fn atomic_write(path: &Path, data: &[u8]) -> std::io::Result<()> {
    let tmp = path.with_extension("tmp");
    let mut f = File::create(&tmp)?;
    f.write_all(data)?;
    f.sync_all()?; // the new contents are on stable storage before the rename
    fs::rename(&tmp, path)?;
    // make the rename durable too: sync the directory
    File::open(path.parent().unwrap_or(Path::new(".")))?.sync_all()?;
    Ok(())
}

/// A tiny checksum (FNV-1a) standing in for CRC32: a page with a different checksum was torn or corrupted.
fn checksum(bytes: &[u8]) -> u64 {
    bytes.iter().fold(0xcbf2_9ce4_8422_2325u64, |h, b| (h ^ *b as u64).wrapping_mul(0x0000_0100_0000_01b3))
}

#[test]
fn a_replaced_file_holds_the_new_contents_and_leaves_no_temp_file() {
    let dir = std::env::temp_dir().join(format!("anneal-durability-{}", std::process::id()));
    fs::create_dir_all(&dir).unwrap();
    let path = dir.join("manifest");
    atomic_write(&path, b"v1").unwrap();
    atomic_write(&path, b"v2 longer").unwrap();
    assert_eq!(fs::read(&path).unwrap(), b"v2 longer");
    assert!(!path.with_extension("tmp").exists());
    fs::remove_dir_all(&dir).unwrap();
}

#[test]
fn a_torn_page_has_the_wrong_checksum() {
    let mut page = vec![7u8; 4096];
    let stored = checksum(&page);
    page[2048..].fill(0); // the second half never reached the disk
    assert_ne!(checksum(&page), stored, "recovery notices and repairs it from the log");
    assert_eq!(checksum(&vec![7u8; 4096]), stored);
}
```

### Using it: a log written before the data

```rust test
use std::fs::OpenOptions;
use std::io::{Read, Write};

/// Appends a record to the log and makes it durable before returning: only then may the caller change the data page.
fn log_append(log: &mut std::fs::File, record: &str) -> std::io::Result<()> {
    writeln!(log, "{record}")?;
    log.sync_data()
}

#[test]
fn replaying_the_log_rebuilds_the_state_a_crash_lost() {
    let path = std::env::temp_dir().join(format!("anneal-wal-{}", std::process::id()));
    let mut log = OpenOptions::new().create(true).append(true).open(&path).unwrap();
    for rec in ["set a=1", "set b=2", "set a=3"] {
        log_append(&mut log, rec).unwrap();
    }
    drop(log); // "crash": the data pages were never written
    let mut text = String::new();
    std::fs::File::open(&path).unwrap().read_to_string(&mut text).unwrap();
    let mut state = std::collections::BTreeMap::new();
    for line in text.lines() {
        let (k, v) = line.strip_prefix("set ").unwrap().split_once('=').unwrap();
        state.insert(k.to_string(), v.to_string());
    }
    assert_eq!(state["a"], "3");
    assert_eq!(state["b"], "2");
    std::fs::remove_file(&path).unwrap();
}

#[test]
fn flush_on_a_plain_file_is_a_no_op_and_sync_is_not() {
    let path = std::env::temp_dir().join(format!("anneal-flush-{}", std::process::id()));
    let mut f = std::fs::File::create(&path).unwrap();
    f.write_all(b"x").unwrap();
    f.flush().unwrap(); // does nothing for a File
    f.sync_all().unwrap(); // this is the durable one
    assert_eq!(std::fs::metadata(&path).unwrap().len(), 1);
    std::fs::remove_file(&path).unwrap();
}
```

### In the exercises

- **1a-05:** the disk manager's log file and `write_log`.
- **1f-03:** the buffer pool flushes a dirty page before eviction.
- **1a-08:** `shut_down` syncs and closes the files.

### Where it is used

- **PostgreSQL** (write-ahead log with `fsync`, full-page writes against torn pages), **SQLite** (journal or WAL file, `fsync` ordering documented in "Atomic Commit In SQLite"), **LMDB** (copy-on-write pages, `msync`), **RocksDB** (WAL plus `sync` option per write).
- The "Files are hard" and "Crash consistency" literature (Pillai et al., OSDI 2014) shows how often applications get the ordering wrong.
