Merging two replicas is the union of their add pairs and the union of their removed pairs. That is all, and it is enough: union is commutative (order does not matter), associative (grouping does not matter) and idempotent (merging twice changes nothing), so replicas that have heard the same updates in any order are equal. A remove on one replica only killed pairs it had seen, so a concurrent add on another replica survives: **add wins**.

> [!CHECK] Replica A adds x (unique id 1) and then removes x. Replica B, at the same time, adds x (unique id 2). After the two replicas merge, is x in the set? Why is this called an observed-remove set?
> ||Yes. A's remove only marked the pair (x, 1), the one it had observed; B's pair (x, 2) was never removed, so x has a live pair. A remove removes only the adds it has seen.||
>
> - What exactly does `remove(x)` mark as removed?
> - What does merge do with the adds and the removed pairs?
> - When is an element in `elements()`?

## The task

In `src/primer/orset.rs`:

- `merge(&other)`: union the adds and union the removed pairs.
- `elements()`: the distinct elements that have at least one live pair (adds that are not removed), each once. (`to_string`, which sorts the elements and prints `{a, b}`, is given.)

## Tests

- Merging brings in adds and removes in both directions.
- A concurrent add beats a remove (BusTub's AddWinsTest).
- Merging twice changes nothing (DoubleMergeTest).
- `elements` lists each element once; `to_string` sorts them.
- Merge order does not matter over three replicas with mixed operations.

## Syntax and methods

```rust
self.adds.extend(other.adds.iter().cloned());
let mut out: Vec<T> = self.adds.iter().filter(|p| !self.removed.contains(p)).map(|p| p.0.clone()).collect();
out.dedup();     // the pairs are ordered by element, so equal elements are adjacent
```

## Notes

**Why add wins.** Replica A adds `x` with id 0 and removes it (id 0 is in `removed`). Replica B adds `x` with id 1. After the merge `adds = {(x,0), (x,1)}` and `removed = {(x,0)}`: `(x,1)` is alive. A did not see B's add when it removed, so its remove cannot have meant it.

**State-based replication.** Replicas exchange whole states and merge them. That tolerates lost, repeated and reordered messages, which is why the idempotence matters: a replica that loads the same saved copy twice must be unchanged.

**`elements` and duplicates.** Several live pairs of one element appear in the pair order next to each other, so `dedup` collapses them.

## In BusTub

`orset.h`: `Merge(const ORSet<T> &other)`: "`Merge changes from another ORSet.`", `Elements() const -> std::vector<T>`: "`Gets all the elements in the set.`" and the tests `MergeTest`, `AddWinsTest`, `DoubleMergeTest`.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::set_union` into a temporary | `BTreeSet::extend` |
| `auto copy_a = student_a_courses;` | `.clone()` |

**Port rule:** a value copy of a replica is `clone()`; merging a snapshot is `merge(&snapshot)`.

## Learn more
- [`BTreeSet::extend`](https://doc.rust-lang.org/std/collections/struct.BTreeSet.html) · [Join-semilattices and CRDTs](https://en.wikipedia.org/wiki/Conflict-free_replicated_data_type#State-based_CRDTs)

## Performance

Merge is linear in the size of the other replica's state. Because states only grow, repeated merging of whole states gets expensive; delta-state CRDTs ship only what changed.

**Measure it.** Merge two replicas with 100 000 pairs each, twice: the second merge changes nothing but still costs the same.

## Hints

### Merge both sets

Merging only the adds would resurrect elements that the other replica removed.

### Don't remove on merge

A merge never deletes anything; removal is recorded by pairs in `removed`.
