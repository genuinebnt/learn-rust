Erasing mirrors inserting: search for the key, remember the update vector, then on every level the node takes part in, make the predecessor skip it. Afterwards the list may have empty top levels, which must be given up, or every later search wastes time walking down empty lanes.

## The task

In `src/primer/skiplist.rs`:

- `SkipList::erase(&key) -> bool`: write lock; search; not found: `false`; for each level `0..node.height()` set `update[level]`'s next to the node's next; free the slot (`release`, given: the arena reuses it); lower the list's height while its top level has no nodes (`height > 1` and the header's link at `height - 1` is empty); size - 1.
- `SkipList::clear()`: write lock; keep only the header (`nodes.truncate(1)`), empty its links, forget the free slots, height 1, size 0.

## Tests

- Erase removes the key and decreases the size; erasing a missing key changes nothing.
- Every level forgets the erased node (sorted, no stale links).
- Slots are reused over many insert/erase rounds.
- Clear empties the list and it can be filled again.
- Erasing the tallest nodes lowers the list's height and later searches still work.

## Syntax and methods

```rust
for level in 0..inner.nodes[id].height() {
    let next = inner.nodes[id].next(level);
    inner.nodes[update[level]].set_next(level, next);
}
inner.release(id);
while inner.height > 1 && inner.nodes[HEADER].next(inner.height - 1).is_none() { inner.height -= 1; }
```

## Notes

**Which levels.** Only levels below the node's height link to it; `update[level]` for higher levels point at other nodes and must not be touched.

**Shrinking.** The invariant is "`height` is the highest level that has any node". Search starts there; a larger value is still correct but slow.

**The arena.** `release` clears a slot and remembers it; the next `insert` reuses it, so repeated insert/erase does not grow `nodes`.

## In BusTub

`skiplist.cpp`: "`Erases the key from the skip list.` ... `@return bool true if the element got erased, false otherwise.`" and `Clear`: "`Removes all elements from the skip list. Note: You might want to use the provided Drop helper function.`" (the Rust arena needs no such helper).

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `Drop()` frees links iteratively to avoid a stack overflow | dropping the arena frees every node in a loop |
| `links_[i] = nullptr` to unlink | `set_next(level, next_of_removed)` |

**Port rule:** an unlink is "predecessor.next = removed.next" on each level; no `delete` needed.

## Learn more
- [`Vec::truncate`](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.truncate) · [`mem::replace`](https://doc.rust-lang.org/std/mem/fn.replace.html)

## Performance

Same expected `O(log n)` as insert. `clear` is `O(n)` in the number of nodes (truncating the arena drops each key). The free list makes insert/erase churn allocation-free once the arena has grown to the working-set size.

**Measure it.** Insert and erase 100 000 keys five times: `nodes.len()` stays near 100 001.

## Hints

### Unlink on the node's own levels only

Loop to the node's height, not the list's.

### Lower the height after unlinking

Check the header's link at the top level; do it in a loop since several levels can empty at once.

### `clear` must also reset the header's links

Truncating the arena leaves the header pointing at slots that no longer exist.
