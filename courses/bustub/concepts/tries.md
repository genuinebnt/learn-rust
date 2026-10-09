---
title: Tries: a tree indexed by the characters of a key
summary: How a trie stores strings by sharing prefixes, how get, put and remove walk it, and why a node can have both a value and children.
minutes: 6
---
A **trie** (prefix tree) stores keys that are strings by spending one tree level per character. The root stands for the empty prefix; the child of a node under character `c` stands for "this prefix followed by `c`". A key's value is stored on the node where its last character leads. Keys that start the same way share nodes, so `te`, `tea` and `ten` use three nodes below `t`.

```svg
caption: A trie holding "te" = 1, "tea" = 2, "ten" = 3 and "to" = 4. A node that ends a key carries a value (marked); the node for "te" has a value and two children.
<svg viewBox="0 0 760 240" role="img" aria-label="A trie with keys te, tea, ten and to">
<defs><marker id="tr-a" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9 z" style="fill:var(--dim)"/></marker></defs>
<circle class="live" cx="380" cy="30" r="16"/><text class="mid fg sm" x="380" y="34">root</text>
<circle class="live" cx="380" cy="90" r="16"/><text class="mid fg sm" x="380" y="94">t</text>
<circle class="hot" cx="300" cy="150" r="16"/><text class="mid fg sm" x="300" y="154">e</text>
<circle class="hot" cx="470" cy="150" r="16"/><text class="mid fg sm" x="470" y="154">o</text>
<circle class="hot" cx="240" cy="210" r="16"/><text class="mid fg sm" x="240" y="214">a</text>
<circle class="hot" cx="360" cy="210" r="16"/><text class="mid fg sm" x="360" y="214">n</text>
<path class="ln" d="M380 46 L380 74" marker-end="url(#tr-a)"/><path class="ln" d="M372 104 L308 136" marker-end="url(#tr-a)"/><path class="ln" d="M388 104 L462 136" marker-end="url(#tr-a)"/>
<path class="ln" d="M292 166 L248 196" marker-end="url(#tr-a)"/><path class="ln" d="M308 166 L352 196" marker-end="url(#tr-a)"/>
<text class="dim sm" x="322" y="150">1</text><text class="dim sm" x="492" y="154">4</text><text class="dim sm" x="262" y="214">2</text><text class="dim sm" x="382" y="214">3</text>
</svg>
```

## The three operations

- **get(key)**: start at the root, follow the child for each character; fail if a child is missing; at the end the node must **carry a value** (a prefix such as `t` above leads somewhere but holds nothing).
- **put(key, value)**: the same walk, creating the missing nodes, then set the value on the last node. The empty key puts the value on the root.
- **remove(key)**: walk to the node, clear its value, then **prune**: a node with no value and no children is dead weight, so it is removed from its parent, and the parent is checked in turn, up to the root.

A node may have both a value and children (`te` above): a key can be a prefix of another. Pruning must stop at such a node.

## Why use one

Lookup costs `O(len(key))` regardless of how many keys are stored, ordered iteration comes for free (children sorted), and *prefix queries* ("all keys starting with `te`") are a subtree walk. Costs: memory (a node per character; real tries compress chains) and cache behaviour (pointer chasing).

## Typed values

BusTub's trie stores values of **any type** under different keys, and `Get<T>` returns nothing if the stored value is not a `T`. In Rust the node stores the value as `Arc<dyn Any + Send + Sync>`; `downcast_ref::<T>()` asks "is it a T?" and answers with `Option<&T>`.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `std::map<char, std::shared_ptr<const TrieNode>> children_` | `BTreeMap<char, Arc<TrieNode>>` |
| `dynamic_cast<const TrieNodeWithValue<T> *>(node)` | `node.value.as_ref()?.downcast_ref::<T>()` |
| `is_value_node_` flag next to a polymorphic node class | `value: Option<Arc<dyn Any + Send + Sync>>`: the option is the flag |

**Port rule:** a class hierarchy used to add one optional field is an `Option` field.

## In real code

### Using it: a small string trie

```rust test
use std::collections::BTreeMap;

#[derive(Default)]
struct Node {
    children: BTreeMap<char, Node>,
    value: Option<u32>,
}

impl Node {
    fn put(&mut self, key: &str, value: u32) {
        let mut node = self;
        for c in key.chars() {
            node = node.children.entry(c).or_default();
        }
        node.value = Some(value);
    }
    fn get(&self, key: &str) -> Option<u32> {
        let mut node = self;
        for c in key.chars() {
            node = node.children.get(&c)?;
        }
        node.value
    }
    /// All values whose key starts with `prefix`, in key order.
    fn with_prefix(&self, prefix: &str) -> Vec<u32> {
        let mut node = self;
        for c in prefix.chars() {
            match node.children.get(&c) {
                Some(n) => node = n,
                None => return vec![],
            }
        }
        let mut out = vec![];
        fn walk(n: &Node, out: &mut Vec<u32>) {
            out.extend(n.value);
            for child in n.children.values() {
                walk(child, out);
            }
        }
        walk(node, &mut out);
        out
    }
}

#[test]
fn a_prefix_leads_somewhere_but_holds_nothing() {
    let mut t = Node::default();
    t.put("te", 1);
    t.put("tea", 2);
    assert_eq!(t.get("te"), Some(1));
    assert_eq!(t.get("t"), None);
    assert_eq!(t.get("team"), None);
    assert_eq!(t.get(""), None);
}

#[test]
fn prefix_queries_walk_a_subtree() {
    let mut t = Node::default();
    for (k, v) in [("te", 1), ("tea", 2), ("ten", 3), ("to", 4)] {
        t.put(k, v);
    }
    assert_eq!(t.with_prefix("te"), vec![1, 2, 3]);
    assert_eq!(t.with_prefix("t"), vec![1, 2, 3, 4]);
    assert!(t.with_prefix("x").is_empty());
}
```

### Using it: values of different types behind `Any`

```rust test
use std::any::Any;
use std::collections::HashMap;

#[test]
fn downcasting_answers_only_for_the_stored_type() {
    let mut m: HashMap<&str, Box<dyn Any>> = HashMap::new();
    m.insert("n", Box::new(7u32));
    m.insert("s", Box::new(String::from("seven")));
    assert_eq!(m["n"].downcast_ref::<u32>(), Some(&7));
    assert_eq!(m["n"].downcast_ref::<String>(), None);
    assert_eq!(m["s"].downcast_ref::<String>().map(|s| s.as_str()), Some("seven"));
}

#[test]
fn a_value_that_is_not_clonable_can_live_behind_any() {
    struct NoClone(u32);
    let boxed: Box<dyn Any> = Box::new(NoClone(5));
    assert_eq!(boxed.downcast_ref::<NoClone>().map(|n| n.0), Some(5));
}
```

### In the exercises

- **0a-01:** `Trie::get` and `get_shared`.
- **0a-02:** `put` and `remove`, with pruning.

### Where it is used

- **Autocomplete and spell checking**, **IP routing tables** (longest-prefix match in a binary trie), **Unix path and URL routers** in web frameworks.
- **Radix trees** (compressed tries): Linux's page cache index, Redis's streams, many HTTP routers.
- **Hash array mapped tries** back the persistent maps of Clojure and Scala.
