A trie stores a string key as a path: one node per character, from the root. A **value** sits on the node where the key ends, and it may be of *any* type: the same trie can hold a `u32` under one key and a `String` under another. `get::<T>` asks for the value at a key **as a `T`**, and gets nothing if the key is missing, leads only to longer keys, or holds a value of another type.

## The task

In `src/primer/trie.rs`:

- `Trie::get::<T>(&self, key) -> Option<&T>`: walk from the root along the characters of `key` (each node's `children` map); at the end the node must have a `value`; downcast it to `T` (`downcast_ref`).
- `Trie::get_shared::<T>(&self, key) -> Option<Arc<T>>`: the same walk, but return an owner of the value (`Arc::downcast`) so that the caller can keep it after the trie is gone (the store of stage 4 needs it).

Stage 1 comes before `put`, so the tests build their tries by hand from the given `TrieNode` fields and `Trie::from_root`.

## Tests

- An empty trie finds nothing.
- The value at the end of the key is found; a prefix that holds no value, a key longer than any stored one, and a diverging key are not.
- The requested type must match the stored one.
- The empty key is the root's value; a node can have a value and children at once.
- `get_shared` keeps the value alive after the trie is dropped.

## Syntax and methods

```rust
let mut node = self.root.as_ref()?;              // Option<&Arc<TrieNode>>: no root, no value
for c in key.chars() { node = node.children.get(&c)?; }
node.value.as_ref()?.downcast_ref::<T>()          // Option<&T>
node.value.clone()?.downcast::<T>().ok()          // Option<Arc<T>>
```

## Notes

**`?` is the algorithm.** Every failure in the walk means "not found": a missing child, no value, wrong type. In a function returning `Option`, `?` turns each into an early `None`.

**Type-erased values.** `Arc<dyn Any + Send + Sync>` forgets the concrete type; `downcast_ref::<T>()` checks a hidden type id and returns `None` on a mismatch. That is the Rust counterpart of BusTub's `dynamic_cast<TrieNodeWithValue<T> *>`.

**Keys are `char`s.** BusTub's children are keyed by `char`; here `chars()` yields Unicode scalar values, which for ASCII is the same thing.

## In BusTub

`trie.h`: "`// A Trie is a data structure that maps strings to values of type T. All operations on a Trie should not modify the trie itself. It should reuse the existing nodes as much as possible, and create new nodes to represent the new trie.`" and "`You are NOT allowed to remove any `const` in this project, or use `mutable` to bypass the const checks.`"

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `auto *with_value = dynamic_cast<const TrieNodeWithValue<T> *>(node.get()); if (with_value == nullptr) return nullptr;` | `node.value.as_ref()?.downcast_ref::<T>()` |
| `if (it == children.end()) return nullptr;` | `node.children.get(&c)?` |
| returns `const T *` | returns `Option<&T>` |

**Port rule:** a pointer that may be null is an `Option<&T>`; each null check before use becomes `?`.

## Learn more
- [`Any::downcast_ref`](https://doc.rust-lang.org/std/any/trait.Any.html#method.downcast_ref) · [`Arc::downcast`](https://doc.rust-lang.org/std/sync/struct.Arc.html#method.downcast)

## Performance

`get` is `O(len(key) × log fan-out)`: one ordered-map lookup per character, independent of how many keys the trie holds. Nothing is allocated or locked.

**Measure it.** Look up the same 10-character key in tries of 100 and 1 000 000 keys: the time is the same.

## Hints

### The walk and the check are two steps

Reaching the node for the last character does not mean the key is stored: check the node's value separately.

### Do not unwrap the downcast

A value of another type is a normal answer (`None`), not a bug. Keep the `Option` flowing.
