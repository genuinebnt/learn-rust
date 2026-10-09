A challenge: no walkthrough, no hints, no solution. It is extra practice and does not count towards the course.

## What to build

Nothing new. `src/storage/disk/cached_disk.rs` is a complete page cache in front of any disk. It is meant to be invisible: to everyone using it, it should behave exactly like the disk underneath. It looks right, and it has one bug. Find it with the tests and fix it.

## Why

A cache is a second copy of the truth, and every second copy can go stale. Cache bugs are rarely in the code that reads or writes; they are in the operations that someone forgot to tell the cache about. The same lesson returns with the buffer pool in module 1f, where a stale page is a much worse failure.

## The contract

A `CachedDisk` answers every read, write and delete exactly as the disk underneath would, whatever its capacity. It writes through: the disk underneath is always current. It saves reads, nothing else.

## What the tests check

- A page just written is served from memory.
- A full cache forgets old pages without losing data.
- A deleted page reads as zeros, and the cache and the disk underneath agree.
- A property over random sequences of writes, reads and deletes, compared with a plain map of pages.

## Done when

All the `s1a_c2` tests pass, and you can say in one sentence what the bug was.
