`remove` returns a trie without the value under a key. Like `put` it copies only the path. Unlike `put` it has a second job: after clearing the value, a node that holds no value and has no children is useless and must be **pruned**, and so must its parent if that now leads nowhere either. If the whole trie becomes empty it has **no root**.

## The task

In `src/primer/trie.rs`: `Trie::remove(&self, key) -> Trie`, with the helper `remove_at(node, key) -> Removal` in the same region. `Removal` is `Missing` (no value under the key: the answer is the old trie, unchanged) or `Replaced(Option<Arc<TrieNode>>)` (the node that takes this position: `None` if nothing is left of it). For each node on the path: clone it, recurse into the child (or clear the value at the end of the key), then put the replacement child back, drop the child if it became `None`, and return `None` yourself if you now have no value and no children.

## Tests

- Only the given key disappears; the others stay.
- Removing everything leaves a trie with no root.
- Nodes with no value and no children are pruned; a node that still leads somewhere stays.
- Removing a missing key changes nothing.
- Removing never changes the old version.

## Syntax and methods

```rust
enum Removal { Missing, Replaced(Option<Arc<TrieNode>>) }
match Self::remove_at(child, rest) {
    Removal::Missing => return Removal::Missing,
    Removal::Replaced(Some(c)) => { new.children.insert(*c_char, c); }
    Removal::Replaced(None) => { new.children.remove(c_char); }
}
```

## Notes

**Why a result type.** Two different "nothing" answers must not be confused: *the key was not there* (keep the whole old trie, all pointers shared) and *the subtree is now empty* (the parent must forget it). Returning `None` for both would make the parent either copy a path for nothing or keep an empty node.

**Pruning is why the tests look at `root()`.** After `remove("te")` of the last key the root must be `None`, not an empty node: BusTub's `RemoveFreeTest` asserts exactly this.

**A value node with children stays.** Removing `te` from `{te, tes, test}` clears the value but the node still has a child; pruning stops there.

## In BusTub

`trie.cpp` for `Remove`: the starter comment says to return a new trie and, in the tests, `RemoveFreeTest`: "`ASSERT_EQ(trie.GetRoot()->children_.at('t')->children_.at('e')->children_.size(), 0); trie = trie.Remove("te"); ASSERT_EQ(trie.GetRoot(), nullptr);`".

## The C/C++ way

| C / C++ | Rust |
|---|---|
| return `nullptr` for a pruned child, and a separate "found" flag | `Removal::Replaced(None)` vs `Removal::Missing` |
| `new_node->children_.erase(c)` | `new.children.remove(c)` |
| copying a `TrieNode` without its value to clear it | clone and set `value = None` |

**Port rule:** when a recursive helper has two kinds of "no", give it a two-case return type.

## Learn more
- [Rust enums](https://doc.rust-lang.org/book/ch06-01-defining-an-enum.html) · [Deletion in tries](https://en.wikipedia.org/wiki/Trie#Deletion)

## Performance

Same as `put`: one clone per node on the path. A removal that prunes allocates fewer nodes than it visits (the pruned ones are not recreated), so a trie that is emptied step by step shrinks, which a "just clear the value" version would not.

**Measure it.** Insert 10 000 keys then remove them all; the final root is `None`. Without pruning it would be a trie of empty nodes.

## Hints

### Report 'missing' before copying

If the key is not stored, return `Missing` as soon as the walk fails or the last node has no value, so that the caller keeps the old pointer.

### Decide pruning at the end of each level

After updating the clone's children and value, a node with `value.is_none() && children.is_empty()` is gone: return `Replaced(None)`.

### The root is just another node

The same helper handles the root; a trie whose root is pruned is `Trie::from_root(None)`.
