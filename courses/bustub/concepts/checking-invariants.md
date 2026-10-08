---
title: Invariants: stating what must always be true, and checking it
summary: How to write a data structure's invariants down, turn them into a checker you can call from tests and debug builds, and what a violation looks like when you have not.
minutes: 8
---
Every stage from here on builds a structure with rules that must hold between operations: the free list and page table partition the slots, ARC's four lists stay within `c` and `2c`, a hash table's directory entries point at buckets whose local depth matches. Bugs in these structures are almost always **invariant violations**: one operation leaves the structure in a state no other operation expects.

## Write the invariants as a list first

For ARC, in words:

1. A frame is on exactly one of `mru`, `mfu`; a page is on at most one ghost list; no page is both live and a ghost.
2. `|mru| + |mru_ghost| <= c`, and `|mru| + |mfu| + |mru_ghost| + |mfu_ghost| <= 2c`.
3. Every handle in the maps names a node in the list the map says it is in.
4. `curr_size` equals the number of live evictable frames.

Writing them is half the work. Several of the bugs you will meet are visible the moment you try to put the rule into a sentence.

## Turn them into a function

```rust
#[cfg(debug_assertions)]
fn check(&self) {
    assert!(self.mru.len() + self.mru_ghost.len() <= self.replacer_size, "mru + mru_ghost exceeds c");
    assert!(self.mru.len() + self.mfu.len() + self.mru_ghost.len() + self.mfu_ghost.len() <= 2 * self.replacer_size, "four lists exceed 2c");
    for (frame, alive) in &self.alive {
        assert!(self.list_of(alive.status).get(alive.handle) == Some(frame), "the handle of frame {} is stale", frame.0);
    }
    let evictable = self.alive.values().filter(|a| a.evictable).count();
    assert_eq!(evictable, self.curr_size, "curr_size is out of step");
}
```

Call it at the end of every public method that changes state, under `#[cfg(debug_assertions)]` (or `debug_assert!` inside a helper) so release builds pay nothing. The assertion messages are the point: when a test fails you read *which* rule broke, and the stack shows the last operation, which is the one that broke it.

## Where the check runs

| place | what it buys |
|---|---|
| inside the structure, under `debug_assert!` | the exact operation that broke an invariant, in every test and every model run |
| a public `verify_integrity()` method | tests and the buffer pool can call it; the hash table module makes it part of the API (BusTub's `VerifyIntegrity`) |
| after each step of a model test | together with the comparison against the simple model |
| never in the hot path of release | a full check is O(n); keep it out of production |

## What a violation looks like without a checker

The failure appears *later and elsewhere*: `evict` returns a frame whose page is a ghost, `size()` disagrees with what `evict` can deliver, a handle used after `remove` returns `None` where the code expected `Some`. By then the state that caused it is gone. A checker moves the failure to the cause.

> [!TIP] Invariants, preconditions, postconditions
> A **precondition** is what the caller must guarantee (`remove` requires the frame to be evictable), a **postcondition** is what the method guarantees (the victim is no longer live), and an **invariant** is what holds between every pair of calls. `assert!` the first at the top of the method, `assert!` the second at the bottom, and `check()` the third.
