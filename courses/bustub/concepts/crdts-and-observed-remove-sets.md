---
title: CRDTs and the observed-remove set
summary: How replicas that accept updates independently can merge into the same state in any order, why a plain set cannot do it, and how tagging each add with a unique id makes "add wins" automatic.
minutes: 7
---
Two copies of a shopping cart, on a phone and a laptop, are edited while offline. When they meet, they must end up the same, with no server deciding who is right. A **CRDT** (conflict-free replicated data type) is a data structure designed so that this always works: merging replicas is **commutative** (order does not matter), **associative** (grouping does not matter) and **idempotent** (merging the same thing twice changes nothing). Replicas that have seen the same updates, in any order, are equal.

## Why a plain set fails

Replica A removes `x`; replica B (which never heard of that) adds `x`. Merging "sets" with union brings `x` back (the remove is lost); merging with a rule like "removed wins" loses B's add; and neither rule can tell *this* add from a **different** add of `x` that happened later. The state must record *which* add a remove refers to.

## The observed-remove set (OR-Set)

Give every `add` a **unique id** (a *tag*). An element is represented by the pairs `(element, tag)` that were added. A `remove(x)` removes exactly the pairs for `x` **this replica has seen**, and remembers them in a set of removed pairs.

- `contains(x)`: some pair `(x, tag)` exists and is not removed.
- `merge(other)`: union of the add pairs, union of the removed pairs.

A concurrent add on another replica has a tag this replica's remove never saw, so after the merge that pair is not removed: **add wins** over a concurrent remove. A remove of what you saw is permanent, even if another replica still has the pair, because removal is also merged by union. Adding `x` again later makes a fresh tag, so it is visible again.

```svg
caption: A removes x (killing tag 0) while B concurrently adds x with tag 1. After merging in either direction both replicas hold {(x,0) removed, (x,1) live}: x is present.
<svg viewBox="0 0 760 170" role="img" aria-label="Two replicas merging an add and a remove">
<text class="mid fg sm" x="150" y="30">replica A</text><text class="mid fg sm" x="610" y="30">replica B</text>
<rect class="box" x="60" y="40" width="180" height="50" rx="3"/><text class="mid fg sm" x="150" y="62">adds {(x,0)}</text><text class="mid fg sm" x="150" y="80">removed {(x,0)}</text>
<rect class="box" x="520" y="40" width="180" height="50" rx="3"/><text class="mid fg sm" x="610" y="62">adds {(x,1)}</text><text class="mid fg sm" x="610" y="80">removed {}</text>
<rect class="hot" x="280" y="100" width="200" height="50" rx="3"/><text class="mid fg sm" x="380" y="122">merged: adds {(x,0),(x,1)}</text><text class="mid fg sm" x="380" y="140">removed {(x,0)} → x present</text>
</svg>
```

## Why merging converges

Both parts are sets and merge is union, which is commutative, associative and idempotent. Whatever order messages arrive in, replicas that have received the same updates hold the same pair of sets, and `contains` is a function of that state. This is a **state-based** CRDT (convergent): replicas ship their state. The cost is growth: removed pairs are kept (tombstones). Real systems compact them once all replicas have seen them.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `std::set<std::pair<T, uid_t>>` for both parts | `BTreeSet<(T, Uid)>` (ordered, so equal elements are adjacent) |
| `ORSet<T>` copied for the driver's saved copies | `#[derive(Clone)]`: a replica snapshot is a clone |
| `std::unique_ptr<ORSetNode>` held in a vector and a back-pointer to the driver | the driver owns plain sets in `Vec`s and nodes are indexes |

**Port rule:** a "node with a pointer to its driver" is the driver with a node index; Rust avoids the back-pointer.

## In real code

### Using it: add wins, in a few lines

```rust test
use std::collections::BTreeSet;

#[derive(Clone, Default)]
struct OrSet {
    adds: BTreeSet<(char, u32)>,
    removed: BTreeSet<(char, u32)>,
}

impl OrSet {
    fn add(&mut self, e: char, tag: u32) {
        self.adds.insert((e, tag));
    }
    fn remove(&mut self, e: char) {
        let seen: Vec<_> = self.adds.iter().filter(|p| p.0 == e).cloned().collect();
        self.removed.extend(seen);
    }
    fn contains(&self, e: char) -> bool {
        self.adds.iter().any(|p| p.0 == e && !self.removed.contains(p))
    }
    fn merge(&mut self, other: &OrSet) {
        self.adds.extend(other.adds.iter().cloned());
        self.removed.extend(other.removed.iter().cloned());
    }
}

#[test]
fn a_concurrent_add_beats_a_remove() {
    let (mut a, mut b) = (OrSet::default(), OrSet::default());
    a.add('x', 0);
    a.remove('x');
    b.add('x', 1);
    let (ca, cb) = (a.clone(), b.clone());
    a.merge(&cb);
    b.merge(&ca);
    assert!(a.contains('x') && b.contains('x'));
}

#[test]
fn a_remove_of_what_was_seen_stays_removed_after_merging() {
    let (mut a, mut b) = (OrSet::default(), OrSet::default());
    a.add('x', 0);
    b.merge(&a);
    b.remove('x');
    a.merge(&b);
    assert!(!a.contains('x') && !b.contains('x'));
}
```

### Using it: merge is commutative, associative and idempotent

```rust test
use std::collections::BTreeSet;

type State = BTreeSet<u32>;

fn merge(a: &State, b: &State) -> State {
    a.union(b).cloned().collect()
}

#[test]
fn union_merge_has_the_three_properties() {
    let a: State = [1, 2].into();
    let b: State = [2, 3].into();
    let c: State = [9].into();
    assert_eq!(merge(&a, &b), merge(&b, &a), "commutative");
    assert_eq!(merge(&merge(&a, &b), &c), merge(&a, &merge(&b, &c)), "associative");
    assert_eq!(merge(&a, &a), a, "idempotent");
}

#[test]
fn replicas_that_saw_the_same_updates_are_equal_whatever_the_order() {
    let updates: Vec<State> = vec![[1].into(), [2].into(), [3].into()];
    let fold = |order: &[usize]| order.iter().fold(State::new(), |acc, i| merge(&acc, &updates[*i]));
    assert_eq!(fold(&[0, 1, 2]), fold(&[2, 0, 1]));
}
```

### In the exercises

- **0d-06:** `add`, `remove`, `contains` on one replica.
- **0d-07:** `merge` and `elements`.
- **0d-08:** a network of replicas that save and load each other's state, including a lost network.

### Where it is used

- **Riak** data types, **Redis Enterprise** CRDBs, **Automerge** and **Yjs** (collaborative editing), **SoundCloud**'s Roshi (a last-writer-wins element set).
- **Shapiro, Preguiça, Baquero, Zawirski**, "A comprehensive study of Convergent and Commutative Replicated Data Types" (2011) defines the OR-Set.
