---
title: Latching a three-level index: header, directory, bucket
summary: Which latch each level takes in each mode, why a parent is released only after its child is held, what the insert path holds across a split, and the deadlock-free order the tests exercise.
minutes: 10
---
The hash table is shared. Many threads look up and insert at once, and a split changes the directory under a lookup's feet. The pool already gives every page a reader-writer latch (module 1g); this page is the **protocol** for using them on a path from the root to a leaf, which the B+ tree in module 2c reuses almost unchanged.

## The path and the modes

A lookup walks **header → directory → bucket**. Each step is a page, so each step takes that page's latch. Which mode?

| operation | header | directory | bucket |
|---|---|---|---|
| `get_value` | read | read | read |
| `insert` | read (write if it must create a directory) | **write** (a split may change it) | write |
| `remove` | read | **write** (a merge may change it) | write |

Reads share; writers exclude. The `insert` and `remove` paths take the *directory* in write mode up front, because they cannot know until they have looked at the bucket whether a split or merge will follow, and upgrading a read latch to a write latch is not possible without releasing it (a gap where the bucket may change).

## Latch crabbing: take the child, then let go of the parent

```rust
let directory_guard = self.bpm.write_page(directory_page_id);   // child latched...
drop(header_guard);                                              // ...now the parent can go
let bucket_guard = self.bpm.write_page(bucket_page_id);
// the directory stays latched while the bucket may be split
```

The walk **holds the parent until the child is latched**, then releases the parent: the hand-over-hand pattern called **crabbing**. Releasing the parent *before* taking the child would leave a gap in which the header's pointer could change to a different directory. And it releases the parent *as soon as it is safe*, so other threads can use it: a lookup that has the directory and the bucket need not keep the header.

When is a parent "safe" to release? When the child **cannot change the parent**: a bucket with room cannot split, so the directory above it will not be modified. This hash table is coarse (the insert holds the directory for the whole operation); the B+ tree release rule is finer: release all ancestors when the child is *safe* (it will not split or merge).

```svg
caption: Hand-over-hand along the path. Each row is one moment: the header is latched first; then the directory is latched while the header is still held, and only then is the header released; then the bucket is latched with the directory kept (a split may change it).
<svg viewBox="0 0 760 240" role="img" aria-label="Three steps of latch crabbing across header, directory and bucket pages">
<text class="big" x="20" y="48">t1</text><text class="big" x="20" y="108">t2</text><text class="big" x="20" y="168">t3</text>
<rect class="hot" x="80" y="26" width="170" height="36" rx="4"/><text class="mid t-a sm" x="165" y="48">header: latched</text>
<rect class="never" x="270" y="26" width="170" height="36" rx="4"/><text class="mid dim sm" x="355" y="48">directory</text>
<rect class="never" x="460" y="26" width="170" height="36" rx="4"/><text class="mid dim sm" x="545" y="48">bucket</text>
<rect class="hot" x="80" y="86" width="170" height="36" rx="4"/><text class="mid t-a sm" x="165" y="108">header: still held</text>
<rect class="live" x="270" y="86" width="170" height="36" rx="4"/><text class="mid t-g sm" x="355" y="108">directory: latched</text>
<rect class="never" x="460" y="86" width="170" height="36" rx="4"/><text class="mid dim sm" x="545" y="108">bucket</text>
<rect class="never" x="80" y="146" width="170" height="36" rx="4"/><text class="mid dim sm" x="165" y="168">header: released</text>
<rect class="live" x="270" y="146" width="170" height="36" rx="4"/><text class="mid t-g sm" x="355" y="168">directory: held</text>
<rect class="live" x="460" y="146" width="170" height="36" rx="4"/><text class="mid t-g sm" x="545" y="168">bucket: latched</text>
<text class="t-w sm" x="650" y="108">the child is held</text><text class="t-w sm" x="650" y="124">before the parent</text><text class="t-w sm" x="650" y="140">is released</text>
<text class="dim sm" x="80" y="214">a thread that inserts into another directory can now take the header: parents are released as early as is safe</text>
</svg>
```

## Rules the tests check

- **Consistent order**: always header, then directory, then bucket, and for two buckets (a merge), the lower slot first. No thread ever waits for an earlier page while holding a later one, so there is no cycle (see the deadlock concept).
- **Hold the directory across a split**: nobody can read the directory half-updated.
- **Drop the bucket guard before deleting its page**: `delete_page` refuses a pinned page, and the guard holds a pin. Dropping first is what makes the delete succeed (and an insert-merge path that forgets it leaks a page).
- **Release on every path**: guards do this by themselves, including on early `return false`: the RAII payoff.

## What this costs, and the finer alternatives

| design | concurrency | complexity |
|---|---|---|
| one latch for the whole table | none | trivial |
| **crabbing with the directory held for the operation** (this course) | readers parallel; writers serialise per directory | moderate |
| latch the bucket only, optimistic directory read | high | needs a version/validation step (retry on change) |
| lock-free | highest | very hard |

The concurrency tests run several threads inserting and reading at once and check that nothing deadlocks and `verify_integrity` still holds afterwards. A timeout that reports "stuck" is part of the test, because the failure mode of a wrong latch order is not a wrong answer: it is silence.

> [!TIP] Pin counts as a leak detector
> After any test, every page's pin count should be zero (`get_pin_count`). A path that returns early while still holding a guard shows up there immediately, long before it starves the pool.
