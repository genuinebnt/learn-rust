`put` returns a **new trie** with a value under a key and leaves the old trie as it was. The new trie must not copy the whole old one: it creates new nodes only along the path from the root to the key and **shares** every other node with the old version.

## The task

In `src/primer/trie.rs`: `Trie::put::<T>(&self, key, value: T) -> Trie`. The recursive helper `put_at(node, key, value)` is part of the region: given the old node at this position (if any) and the rest of the key, it returns the new node:

- start from a **clone** of the old node (its children map clones the child `Arc`s, not the subtrees) or from an empty node if there is none;
- if the key is used up, set `value` on the clone (replacing what was there, whatever its type);
- otherwise replace the clone's child for the next character by the result of the recursive call on the old child;
- wrap the result in `Arc::new`.

The empty key puts the value in the root.

## Tests

- One node per character; the last holds the value.
- Replacing a value, even with another type; keys that are prefixes of each other share a path.
- Putting never changes the old version, and overwriting keeps other versions' values.
- Only the path is copied: siblings and other branches are the same `Arc` (`Arc::ptr_eq`).
- Values need not be clonable and an untouched key's value keeps its address.

## Syntax and methods

```rust
let mut new = node.map(|n| (**n).clone()).unwrap_or_default();   // clone the node inside the Arc
match key.split_first() { None => ..., Some((c, rest)) => ... }
new.children.insert(*c, child);                                  // replace one child pointer
Arc::new(new)
```

## Notes

**Why the value is not copied.** The value sits behind its own `Arc`; cloning a node copies the pointer. That is why `put::<T>` works for a `T` that cannot be cloned at all (a `Box` of a type with no `Clone`): the value is moved into the `Arc` once and shared from then on.

**What gets copied.** On the path: one clone per node, each copying that node's child table (pointers). Everything hanging off the path is untouched. For a 10-character key in a trie of a million keys, a `put` allocates 11 nodes.

**Shared means immutable.** `Arc<TrieNode>` gives only `&TrieNode`: there is no way to change a shared node by mistake. This is the property C++ asks you to keep by never removing `const`.

## In BusTub

`trie.h`: "`// Create a new trie with the given root.`", `Put`: "`template <class T> auto Put(std::string_view key, T value) const -> Trie;`" and the tests `CopyOnWriteTest1`, `2`, `3` (old versions stay intact), `PointerStability` (the value of an untouched key keeps its address) and `NonCopyableTest`.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `node->Clone()` (a virtual method so that nodes with values copy their value) | `(**n).clone()`: derived `Clone`; the value is an `Arc`, so copying it is a pointer copy |
| `std::make_shared<const TrieNode>(...)` | `Arc::new(...)` |
| `std::move(value)` into a `shared_ptr<T>` | `Arc::new(value)`: moved, never copied |

**Port rule:** "clone, then modify the clone" is the whole copy-on-write protocol; shared data is never touched in place.

## Learn more
- [`Arc::ptr_eq`](https://doc.rust-lang.org/std/sync/struct.Arc.html#method.ptr_eq) · [`slice::split_first`](https://doc.rust-lang.org/std/primitive.slice.html#method.split_first)

## Performance

`put` is `O(len(key) × fan-out)` time and allocates `len(key) + 1` nodes, each the size of its child table. Old versions cost nothing extra: sharing means a million snapshots of one trie are a million root pointers plus the paths that changed.

**Measure it.** Put 23 333 keys one by one and keep every version: it takes about 15 ms in release mode, and memory grows by roughly one path per put, not by the size of the trie.

## Hints

### Recurse on the old child, not on the new node

The clone already has the child pointers; look the child up in the **old** node (`node.children.get(c)`) and replace it with the recursive result.

### An absent node is just an empty node

For a key that extends beyond the existing trie, `put_at(None, rest, value)` builds a fresh chain; there is no separate "create" code path.

### Check sharing in your own test

`Arc::ptr_eq(&old.children[&'x'], &new.children[&'x'])` must hold for every branch off the path.
