An **observed-remove set** is a set that can be copied to other machines, edited there, and merged back without a coordinator. The model: every `add(elem, uid)` creates a pair `(elem, uid)` with a unique id; a `remove(elem)` kills the pairs for `elem` **that this replica has seen**; an element is present while one of its pairs is alive. This stage builds one replica; the next stage merges them.

## The task

In `src/primer/orset.rs` (`ORSet<T>` has `adds`, a set of `(T, uid)` pairs, and `removed`, the pairs that were removed):

- `add(elem, uid)`: remember the pair.
- `remove(elem)`: mark every pair for `elem` that is currently in `adds` as removed.
- `contains(elem)`: is there a pair for `elem` in `adds` that is not in `removed`?

## Tests

- Add and remove on one replica.
- Adding an element twice under two ids needs one remove to delete it.
- Adding back after a remove works (a new id).
- Removing an absent element is harmless and does not block a later add.
- Other elements are not affected.

## Syntax and methods

```rust
self.adds.insert((elem.clone(), uid));
let seen: Vec<(T, Uid)> = self.adds.iter().filter(|pair| pair.0 == *elem).cloned().collect();
self.removed.extend(seen);
self.adds.iter().any(|pair| pair.0 == *elem && !self.removed.contains(pair))
```

## Notes

**Why remove copies the pairs.** `remove` must record *which* adds it killed, not "elem is gone": a later add has a new id and is not killed. Removing an element that is not (yet) there kills nothing, so a later add stays visible.

**Collect before extending.** Iterating `adds` while inserting into `removed` is fine (different sets), but collecting first keeps the borrow simple.

**Ordered pairs.** `BTreeSet<(T, Uid)>` sorts by element first, so all pairs of one element are adjacent; stage 7's `elements` uses that.

## In BusTub

`orset.h`: "`/** @brief The observed remove set datatype. */`", `Add(const T &elem, uid_t uid)`: "`uid: unique token associated with the add operation.`", `Remove(const T &elem)`: "`Removes an element from the set if it exists.`".

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::set<std::pair<T, uid_t>>` | `BTreeSet<(T, i64)>` |
| `throw NotImplementedException` in the starter | `todo!()` |

**Port rule:** a set of pairs is a `BTreeSet` of tuples; tuples order lexicographically.

## Learn more
- [OR-Set](https://github.com/pfrazee/crdt_notes#or-set) · [Shapiro et al. 2011](https://inria.hal.science/inria-00555588/document)

## Performance

`contains` and `remove` scan the pairs of the whole set here (`O(n)`); a map from element to its pairs would make them `O(pairs of that element)`. The sets only grow (removed pairs are kept), which real systems compact.

**Measure it.** Add and remove the same element 100 000 times under new ids: the state grows by two pairs per round.

## Hints

### Remove looks at `adds`, not at `removed`

You can only kill what you have seen: the pairs currently in `adds`.

### `contains` needs both sets

A pair counts only if it is in `adds` and not in `removed`.
