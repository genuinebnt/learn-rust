---
title: Persistent data structures: updates that never change the old version
summary: How a tree can return a new version on every update by copying only the path to the change and sharing the rest, why that makes snapshots free, and how Rust's Arc makes the sharing safe.
minutes: 8
---
An ordinary `insert` changes a structure. A **persistent** (or *immutable*) structure's `insert` returns a **new version** and leaves the old one untouched. Both versions are usable afterwards: a reader holding the old one is unaffected by writers, which is the property a database wants from a snapshot.

Copying everything on every update would be absurd. The trick is **path copying**: an update to a tree changes one node, so only that node and its ancestors (the path from the root) need new copies; every other node is shared between the old and the new version.

```svg
caption: put("tea") into a trie holding "te" and "to". The three nodes on the path (root, t, e) are copied; the "o" branch is shared, so both versions point to the same node.
<svg viewBox="0 0 760 230" role="img" aria-label="Two versions of a trie sharing an unchanged branch">
<defs><marker id="pp-a" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9 z" style="fill:var(--dim)"/></marker></defs>
<text class="mid dim sm" x="150" y="22">old version</text><text class="mid dim sm" x="580" y="22">new version</text>
<circle class="live" cx="150" cy="55" r="16"/><text class="mid fg sm" x="150" y="59">root</text>
<circle class="live" cx="150" cy="115" r="16"/><text class="mid fg sm" x="150" y="119">t</text>
<circle class="live" cx="90" cy="180" r="16"/><text class="mid fg sm" x="90" y="184">e</text>
<circle class="blue" cx="215" cy="180" r="16"/><text class="mid fg sm" x="215" y="184">o</text>
<circle class="hot" cx="580" cy="55" r="16"/><text class="mid fg sm" x="580" y="59">root'</text>
<circle class="hot" cx="580" cy="115" r="16"/><text class="mid fg sm" x="580" y="119">t'</text>
<circle class="hot" cx="520" cy="180" r="16"/><text class="mid fg sm" x="520" y="184">e'</text>
<circle class="hot" cx="450" cy="215" r="14"/><text class="mid fg sm" x="450" y="219">a</text>
<path class="ln" d="M150 71 L150 99" marker-end="url(#pp-a)"/><path class="ln" d="M140 129 L100 165" marker-end="url(#pp-a)"/><path class="ln" d="M160 129 L205 165" marker-end="url(#pp-a)"/>
<path class="ln" d="M580 71 L580 99" marker-end="url(#pp-a)"/><path class="ln" d="M570 129 L530 165" marker-end="url(#pp-a)"/><path class="ln" d="M515 195 L460 205" marker-end="url(#pp-a)"/>
<path class="ln" d="M590 129 C500 140 330 150 232 175" marker-end="url(#pp-a)"/>
<text class="mid dim sm" x="380" y="170">shared</text>
</svg>
```

## The recursion

A persistent `put` is a recursive function that returns the new node for a position:

```text
put(node, key, value):
    new = clone of node (or an empty node if there is none)
    if the key is used up: new.value = value
    else: new.children[c] = put(node.children[c], rest of key, value)
    return new
```

Only nodes on the path are cloned; cloning a node copies its table of child *pointers*, not the subtrees they point to. `remove` is the same shape, plus **pruning**: a node left with no value and no children is not returned, so its parent drops the link.

## What makes the sharing safe

Shared nodes must never change, and must stay alive as long as any version uses them. In C++ that is `shared_ptr<const Node>`; in Rust, `Arc<Node>`: reference counted and, with no `Mutex`, **immutable** (`Arc` gives only `&Node`). The compiler therefore enforces what the C++ code must promise: nothing can mutate a shared node. A version is just a pointer to its root; dropping the last version that uses a node frees it.

## Costs

An update allocates `O(length of the key)` nodes; each clone copies the node's child table (`O(fan-out)` for a map). In return: snapshots cost one pointer copy, readers need no lock on the structure itself, and old versions can be kept for as long as you like. This is how Clojure's vectors and maps, Git's tree objects, and the Merkle trees of many databases work.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `std::shared_ptr<const TrieNode>` with the rule "never remove the `const`" | `Arc<TrieNode>`: shared and immutable by construction |
| `Clone()` virtual method so that `TrieNodeWithValue<T>` copies its value | `#[derive(Clone)]` on a node whose value is an `Option<Arc<dyn Any>>`: cloning copies a pointer |
| `std::make_shared<TrieNode>(*node)` | `Arc::new((**node).clone())` |

**Port rule:** share by cloning the `Arc` (a refcount bump), copy by cloning the node inside it; do the second only on the path being changed.

## In real code

### Using it: a persistent list and its versions

```rust test
use std::sync::Arc;

/// A persistent stack: every `push` returns a new list sharing the old one as its tail.
#[derive(Clone)]
struct List {
    head: Option<Arc<Node>>,
}

struct Node {
    value: i32,
    next: Option<Arc<Node>>,
}

impl List {
    fn new() -> List {
        List { head: None }
    }
    fn push(&self, value: i32) -> List {
        List { head: Some(Arc::new(Node { value, next: self.head.clone() })) }
    }
    fn to_vec(&self) -> Vec<i32> {
        let mut out = vec![];
        let mut cur = &self.head;
        while let Some(n) = cur {
            out.push(n.value);
            cur = &n.next;
        }
        out
    }
}

#[test]
fn versions_share_their_tails() {
    let one = List::new().push(1);
    let two = one.push(2);
    let other = one.push(3);
    assert_eq!(two.to_vec(), vec![2, 1]);
    assert_eq!(other.to_vec(), vec![3, 1]);
    assert_eq!(one.to_vec(), vec![1], "the old version is unchanged");
    assert!(Arc::ptr_eq(two.head.as_ref().unwrap().next.as_ref().unwrap(), one.head.as_ref().unwrap()));
}

#[test]
fn dropping_a_version_keeps_what_others_use() {
    let base = List::new().push(1).push(2);
    let a = base.push(3);
    drop(base);
    assert_eq!(a.to_vec(), vec![3, 2, 1]);
    assert_eq!(Arc::strong_count(a.head.as_ref().unwrap().next.as_ref().unwrap()), 1, "only a's node points at the old head now");
}
```

### Using it: path copying in a small binary tree

```rust test
use std::sync::Arc;

struct Node {
    key: i32,
    left: Option<Arc<Node>>,
    right: Option<Arc<Node>>,
}

/// A new tree with `key` inserted; only the nodes on the path are new.
fn insert(node: &Option<Arc<Node>>, key: i32) -> Option<Arc<Node>> {
    Some(Arc::new(match node {
        None => Node { key, left: None, right: None },
        Some(n) if key < n.key => Node { key: n.key, left: insert(&n.left, key), right: n.right.clone() },
        Some(n) if key > n.key => Node { key: n.key, left: n.left.clone(), right: insert(&n.right, key) },
        Some(n) => Node { key: n.key, left: n.left.clone(), right: n.right.clone() },
    }))
}

#[test]
fn an_insert_copies_one_path_and_shares_the_rest() {
    let mut t = None;
    for k in [5, 2, 8, 1, 9] {
        t = insert(&t, k);
    }
    let t2 = insert(&t, 3); // goes 5 -> 2 -> right of 2
    let (old, new) = (t.as_ref().unwrap(), t2.as_ref().unwrap());
    assert!(!Arc::ptr_eq(old, new));
    assert!(Arc::ptr_eq(old.right.as_ref().unwrap(), new.right.as_ref().unwrap()), "the 8 subtree is shared");
    let (old2, new2) = (old.left.as_ref().unwrap(), new.left.as_ref().unwrap());
    assert!(!Arc::ptr_eq(old2, new2));
    assert!(Arc::ptr_eq(old2.left.as_ref().unwrap(), new2.left.as_ref().unwrap()), "the 1 leaf is shared");
}

#[test]
fn inserting_a_present_key_still_gives_a_valid_tree() {
    let t = insert(&insert(&None, 1), 1);
    assert_eq!(t.unwrap().key, 1);
}
```

### In the exercises

- **0a-02:** `Trie::put` and `Trie::remove` copy the path and share everything else; the tests compare node pointers with `Arc::ptr_eq`.
- **0a-03:** `TrieStore` publishes a new version by swapping one pointer.

### Where it is used

- **Git**: a commit's tree objects share every unchanged subtree with the previous commit.
- **Clojure / Scala / Haskell** persistent collections (hash array mapped tries, finger trees) use path copying.
- **Databases**: copy-on-write B-trees (LMDB, BoltDB) copy the path from leaf to root on every write, and the old root is a consistent snapshot.
