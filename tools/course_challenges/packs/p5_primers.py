from _c import C
M0A, M0B, M0C, M0D = "24-the-persistent-trie", "25-the-skip-list", "26-robin-hood-hashing", "27-sketches-and-crdts"
CH = []

CH.append(C("0a-c1", M0A, "90-challenge-longest-prefix-match", "build", "Challenge: longest prefix match", "easy", "stages_0a::s0a_c1",
  ["routing by the longest matching prefix","comparing a trie-based answer with a brute-force one"],
  ["tries","model-based-testing"],
  "`PrefixTable` in `src/primer/prefix_table.rs`: a table of bit-string prefixes (`\"1010\"`, `\"\"`, ...) with a value each. `lookup(address)` returns the entry whose prefix is the **longest** prefix of the address bit string.",
  "IP routers, URL routers, phone-number switches and `LIKE 'abc%'` indexes all answer \"which of these prefixes is the longest one that matches\". A trie answers it in time proportional to the address length, whatever the number of entries; the *longest* part is what makes it more than a membership test.",
  ["`insert(prefix, value)` replaces the value of an existing prefix and returns the old one. Prefixes and addresses contain only `0` and `1`; the empty prefix matches everything.","`lookup(address)` returns `Some((prefix, value))` for the longest stored prefix that is a prefix of `address`, or `None`.","`remove(prefix)` deletes an entry."],
  ["A returned prefix is a prefix of the address.","No stored prefix that is a prefix of the address is longer than the returned one."],
  ["Adding a longer matching prefix changes the answer to it; adding a shorter or non-matching one never does.","Removing the answered entry falls back to the next longest.","`lookup(a)` and `lookup(b)` for addresses sharing their first `n` bits return the same entry if it is at most `n` long."],
  ["table {\"\": A, \"10\": B, \"1011\": C}: lookup \"10110\" -> (\"1011\", C); \"1001\" -> (\"10\", B); \"0\" -> (\"\", A)"],
  ["Longest, shorter and default matches.","Insert, replace, remove.","A property against a scan over all entries."],
  src=("src/primer/prefix_table.rs", '''
//! Longest-prefix matching over bit strings.

use std::collections::BTreeMap;

pub struct PrefixTable<V> {
    // @begin 0a-c1
    entries: BTreeMap<String, V>,
    //~ _table: std::marker::PhantomData<V>,
    // @end
}

impl<V> PrefixTable<V> {
    pub fn new() -> PrefixTable<V> {
        // @begin 0a-c1
        PrefixTable { entries: BTreeMap::new() }
        //~ todo!("0a-c1: an empty table")
        // @end
    }

    pub fn insert(&mut self, prefix: &str, value: V) -> Option<V> {
        // @begin 0a-c1
        self.entries.insert(prefix.to_owned(), value)
        //~ todo!("0a-c1: store the entry, returning the value it replaced")
        // @end
    }

    pub fn remove(&mut self, prefix: &str) -> Option<V> {
        // @begin 0a-c1
        self.entries.remove(prefix)
        //~ todo!("0a-c1: delete the entry")
        // @end
    }

    pub fn len(&self) -> usize {
        // @begin 0a-c1
        self.entries.len()
        //~ todo!("0a-c1: how many entries")
        // @end
    }

    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }

    /// The entry with the longest prefix of `address`.
    pub fn lookup(&self, address: &str) -> Option<(&str, &V)> {
        // @begin 0a-c1
        (0..=address.len()).rev().find_map(|n| self.entries.get_key_value(&address[..n]).map(|(k, v)| (k.as_str(), v)))
        //~ todo!("0a-c1: try the longest prefix of the address first, then shorter ones")
        // @end
    }
}

impl<V> Default for PrefixTable<V> {
    fn default() -> Self {
        PrefixTable::new()
    }
}
'''),
  test=("tests/stages_0a.rs", '''
use bustub::primer::prefix_table::PrefixTable;

fn table() -> PrefixTable<char> {
    let mut t = PrefixTable::new();
    t.insert("", 'A');
    t.insert("10", 'B');
    t.insert("1011", 'C');
    t
}

#[test]
fn s0a_c1_the_longest_matching_prefix_wins() {
    let t = table();
    assert_eq!(t.lookup("10110"), Some(("1011", &'C')));
    assert_eq!(t.lookup("1001"), Some(("10", &'B')));
    assert_eq!(t.lookup("0"), Some(("", &'A')));
    assert_eq!(t.lookup("1011"), Some(("1011", &'C')), "an address equal to a prefix matches it");
}

#[test]
fn s0a_c1_without_a_default_entry_some_addresses_match_nothing() {
    let mut t = PrefixTable::new();
    t.insert("11", 1);
    assert_eq!(t.lookup("10"), None);
    assert_eq!(t.lookup("1"), None, "a prefix longer than the address cannot match");
    assert_eq!(t.lookup("110"), Some(("11", &1)));
}

#[test]
fn s0a_c1_replacing_and_removing() {
    let mut t = table();
    assert_eq!(t.insert("10", 'Z'), Some('B'));
    assert_eq!(t.lookup("100"), Some(("10", &'Z')));
    assert_eq!(t.remove("1011"), Some('C'));
    assert_eq!(t.lookup("10110"), Some(("10", &'Z')), "falls back to the next longest");
    assert_eq!(t.remove("1011"), None);
    assert_eq!(t.len(), 2);
}

#[test]
fn s0a_c1_a_prefix_only_matches_at_the_start_of_the_address() {
    let mut t = PrefixTable::new();
    t.insert("01", 'x');
    assert_eq!(t.lookup("101"), None, "01 occurs inside the address, not at its start");
    assert_eq!(t.lookup("011"), Some(("01", &'x')));
    assert_eq!(t.len(), 1);
}

#[test]
fn s0a_c1_a_prefix_only_matches_at_the_start_of_the_address() {
    let mut t = PrefixTable::new();
    t.insert("01", 'x');
    assert_eq!(t.lookup("101"), None, "01 occurs inside the address, not at its start");
    assert_eq!(t.lookup("011"), Some(("01", &'x')));
    assert_eq!(t.len(), 1);
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: against a scan over every entry for the longest one that is a prefix.
    #[test]
    fn s0a_c1_property_lookup_equals_a_scan(prefixes in proptest::collection::vec("[01]{0,5}", 0..10), addr in "[01]{0,8}") {
        let mut t = PrefixTable::new();
        for (i, p) in prefixes.iter().enumerate() { t.insert(p, i); }
        let mut want: Option<(&str, usize)> = None;
        let mut last: std::collections::BTreeMap<&str, usize> = Default::default();
        for (i, p) in prefixes.iter().enumerate() { last.insert(p.as_str(), i); }
        for (p, &i) in &last { if addr.starts_with(p) && want.is_none_or(|(w, _)| p.len() > w.len()) { want = Some((p, i)); } }
        prop_assert_eq!(t.lookup(&addr).map(|(p, v)| (p, *v)), want);
    }
}
''')))

CH.append(C("0a-c2", M0A, "91-challenge-keys-under-a-prefix", "extend", "Challenge: keys under a prefix", "easy", "stages_0a::s0a_c2",
  ["walking the node type you were given to enumerate what a trie holds","the order a trie's children give for free"],
  ["tries","persistent-data-structures-and-path-copying"],
  "`keys_with_prefix` in `src/primer/trie_extras.rs`: using the **public** node type of your persistent trie (`Trie::root`, `TrieNode::children`, `TrieNode::value`), list every key stored in a trie that starts with `prefix`, in increasing order. It does not change the trie.",
  "A trie that can only answer \"is this key here\" is half a trie: autocomplete, prefix scans and `LIKE 'abc%'` all ask for *everything below a node*. The tree you built already has the answer; the exercise is to walk it, and to notice that `BTreeMap` children make the output sorted without sorting.",
  ["`keys_with_prefix(trie, prefix) -> Vec<String>`: all keys `k` with `k.starts_with(prefix)` for which a value is stored, ascending.","An empty prefix lists every key. A prefix that leads nowhere lists none. The prefix itself is included if it holds a value.","Works on any trie built with your `Trie::put`; reads only."],
  ["The result is sorted and has no duplicates.","Every returned key has a value in the trie and starts with the prefix."],
  ["The result for prefix `p + c` is a subset of the result for `p`.","Putting a key then listing finds it; removing it then listing does not.","The result equals filtering the full key list by `starts_with`."],
  ["keys {a, ab, abc, b}: prefix \"a\" -> [a, ab, abc]; prefix \"ab\" -> [ab, abc]; prefix \"c\" -> []"],
  ["Nested keys, empty prefix, missing prefix.","Old versions still list what they held.","A property against a `BTreeSet`."],
  src=("src/primer/trie_extras.rs", '''
//! Extra queries over your persistent trie, written against its public node type only.

use std::sync::Arc;

use crate::primer::trie::{Trie, TrieNode};

/// Every key in `trie` that starts with `prefix`, in increasing order.
pub fn keys_with_prefix(trie: &Trie, prefix: &str) -> Vec<String> {
    // @begin 0a-c2
    fn walk(node: &Arc<TrieNode>, path: &mut String, out: &mut Vec<String>) {
        if node.value.is_some() {
            out.push(path.clone());
        }
        for (c, child) in &node.children {
            path.push(*c);
            walk(child, path, out);
            path.pop();
        }
    }
    let Some(mut node) = trie.root() else { return Vec::new() };
    for c in prefix.chars() {
        match node.children.get(&c) {
            Some(child) => node = child,
            None => return Vec::new(),
        }
    }
    let mut out = Vec::new();
    walk(node, &mut prefix.to_owned(), &mut out);
    out
    //~ todo!("0a-c2: follow the prefix down, then collect every value below, children in order")
    // @end
}
'''),
  test=("tests/stages_0a.rs", '''
use bustub::primer::trie::Trie;
use bustub::primer::trie_extras::keys_with_prefix;
use std::collections::BTreeSet;

fn build(keys: &[&str]) -> Trie {
    keys.iter().fold(Trie::new(), |t, k| t.put(k, k.len() as u32))
}

#[test]
fn s0a_c2_keys_under_a_prefix_come_out_sorted() {
    let t = build(&["abc", "b", "a", "ab"]);
    assert_eq!(keys_with_prefix(&t, "a"), vec!["a", "ab", "abc"]);
    assert_eq!(keys_with_prefix(&t, "ab"), vec!["ab", "abc"]);
    assert_eq!(keys_with_prefix(&t, ""), vec!["a", "ab", "abc", "b"]);
}

#[test]
fn s0a_c2_a_prefix_that_leads_nowhere_lists_nothing() {
    let t = build(&["abc"]);
    assert_eq!(keys_with_prefix(&t, "x"), Vec::<String>::new());
    assert_eq!(keys_with_prefix(&t, "abcd"), Vec::<String>::new());
    assert_eq!(keys_with_prefix(&Trie::new(), ""), Vec::<String>::new());
}

#[test]
fn s0a_c2_an_interior_node_without_a_value_is_not_a_key() {
    let t = build(&["abc"]);
    assert_eq!(keys_with_prefix(&t, "a"), vec!["abc"]);
    assert_eq!(keys_with_prefix(&t, "ab"), vec!["abc"]);
}

#[test]
fn s0a_c2_old_versions_keep_their_keys() {
    let v1 = build(&["a", "b"]);
    let v2 = v1.put("c", 1u32).remove("a");
    assert_eq!(keys_with_prefix(&v1, ""), vec!["a", "b"]);
    assert_eq!(keys_with_prefix(&v2, ""), vec!["b", "c"]);
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: equals filtering the sorted key set by `starts_with`.
    #[test]
    fn s0a_c2_property_prefix_listing_equals_a_filter(keys in proptest::collection::btree_set("[ab]{0,4}", 0..12), prefix in "[ab]{0,3}") {
        let mut t = Trie::new();
        for k in &keys { t = t.put(k, 1u32); }
        let want: Vec<String> = keys.iter().filter(|k| k.starts_with(&prefix)).cloned().collect();
        prop_assert_eq!(keys_with_prefix(&t, &prefix), want);
        let all: BTreeSet<String> = keys_with_prefix(&t, "").into_iter().collect();
        prop_assert_eq!(all, keys);
    }
}
''')))

CH.append(C("0a-c3", M0A, "92-challenge-how-much-is-shared", "extend", "Challenge: how much is shared", "medium", "stages_0a::s0a_c3",
  ["measuring structural sharing between two versions of a persistent structure","checking that path copying copies only the path"],
  ["persistent-data-structures-and-path-copying","smart-pointers-box-rc-arc"],
  "`node_count` and `shared_nodes` in `src/primer/trie_extras.rs`: `node_count(trie)` counts the nodes of a trie; `shared_nodes(a, b)` counts the nodes that are **the same allocation** in both (`Arc::ptr_eq`), found by walking the two tries together. With these, the tests check that your `put` and `remove` copy only the nodes on one path.",
  "\"Persistent\" is a claim about memory, not about results: a trie that copies everything on every `put` returns the right answers and defeats the purpose. Counting shared nodes is how you test the claim. After one `put` of a key of length `n`, at most `n + 1` nodes may be new; every other node must be the *same* `Arc` as before.",
  ["`node_count(trie)`: nodes reachable from the root (0 for an empty trie).","`shared_nodes(a, b)`: the number of positions where both tries have a node at the same path and the two nodes are the same `Arc` (pointer-equal); a shared node's whole subtree is shared and is counted node by node.","Both read only."],
  ["`shared_nodes(t, t) == node_count(t)`.","`shared_nodes(a, b) <= min(node_count(a), node_count(b))`."],
  ["After `t.put(key, v)`: `node_count(new) - shared_nodes(old, new) <= key.chars().count() + 1`.","After `t.remove(key)` the same bound holds.","Putting an unrelated key into two versions of a trie leaves both new tries sharing everything but their own paths."],
  ["t has 100 keys; t2 = t.put(\"abc\", 1): at most 4 nodes of t2 are not in t"],
  ["Counting; sharing with itself; one change.","The path-length bound for put and remove (this tests *your* implementation).","A property over random tries and keys."],
  src=("src/primer/trie_extras.rs", '''
//! Extra queries over your persistent trie, written against its public node type only.

use std::sync::Arc;

use crate::primer::trie::{Trie, TrieNode};

/// Every key in `trie` that starts with `prefix`, in increasing order.
pub fn keys_with_prefix(trie: &Trie, prefix: &str) -> Vec<String> {
    // @begin 0a-c2
    fn walk(node: &Arc<TrieNode>, path: &mut String, out: &mut Vec<String>) {
        if node.value.is_some() {
            out.push(path.clone());
        }
        for (c, child) in &node.children {
            path.push(*c);
            walk(child, path, out);
            path.pop();
        }
    }
    let Some(mut node) = trie.root() else { return Vec::new() };
    for c in prefix.chars() {
        match node.children.get(&c) {
            Some(child) => node = child,
            None => return Vec::new(),
        }
    }
    let mut out = Vec::new();
    walk(node, &mut prefix.to_owned(), &mut out);
    out
    //~ todo!("0a-c2: follow the prefix down, then collect every value below, children in order")
    // @end
}

fn count(node: &Arc<TrieNode>) -> usize {
    // @begin 0a-c3
    1 + node.children.values().map(count).sum::<usize>()
    //~ todo!("0a-c3: this node and everything below it")
    // @end
}

/// The number of nodes of the trie.
pub fn node_count(trie: &Trie) -> usize {
    // @begin 0a-c3
    trie.root().map_or(0, count)
    //~ todo!("0a-c3: nodes reachable from the root")
    // @end
}

fn shared(a: &Arc<TrieNode>, b: &Arc<TrieNode>) -> usize {
    // @begin 0a-c3
    if Arc::ptr_eq(a, b) {
        return count(a);
    }
    a.children.iter().map(|(c, ca)| b.children.get(c).map_or(0, |cb| shared(ca, cb))).sum()
    //~ todo!("0a-c3: a node that is the same allocation shares its whole subtree; otherwise compare the children with the same letter")
    // @end
}

/// How many nodes the two tries have in common (the same allocation at the same path).
pub fn shared_nodes(a: &Trie, b: &Trie) -> usize {
    // @begin 0a-c3
    match (a.root(), b.root()) {
        (Some(x), Some(y)) => shared(x, y),
        _ => 0,
    }
    //~ todo!("0a-c3: walk both tries together")
    // @end
}
'''),
  test=("tests/stages_0a.rs", '''
use bustub::primer::trie::Trie;
use bustub::primer::trie_extras::{node_count, shared_nodes};

fn build(keys: &[&str]) -> Trie {
    keys.iter().fold(Trie::new(), |t, k| t.put(k, 1u32))
}

#[test]
fn s0a_c3_counting_nodes() {
    assert_eq!(node_count(&Trie::new()), 0);
    assert_eq!(node_count(&build(&["abc"])), 4, "the root and three letters");
    assert_eq!(node_count(&build(&["abc", "abd", "x"])), 1 + 4 + 1);
}

#[test]
fn s0a_c3_a_trie_shares_everything_with_itself_and_nothing_with_an_empty_one() {
    let t = build(&["a", "ab", "b"]);
    assert_eq!(shared_nodes(&t, &t), node_count(&t));
    assert_eq!(shared_nodes(&t, &Trie::new()), 0);
}

#[test]
fn s0a_c3_one_put_copies_only_the_path() {
    let keys: Vec<String> = (0..60).map(|i| format!("{:03}{}", i, i % 7)).collect();
    let refs: Vec<&str> = keys.iter().map(String::as_str).collect();
    let old = build(&refs);
    let new = old.put("0123456", 9u32);
    let fresh = node_count(&new) - shared_nodes(&old, &new);
    assert!(fresh <= "0123456".len() + 1, "{fresh} nodes are new but the path has {}: put copied more than the path", "0123456".len() + 1);
    assert!(shared_nodes(&old, &new) > 50, "almost everything must be shared");
}

#[test]
fn s0a_c3_removing_a_key_also_copies_only_the_path() {
    let old = build(&["alpha", "alps", "beta", "gamma", "delta", "alphabet"]);
    let new = old.remove("alps");
    assert!(node_count(&new) - shared_nodes(&old, &new) <= "alps".len() + 1);
}

#[test]
fn s0a_c3_two_versions_of_a_trie_share_what_neither_changed() {
    let base = build(&["a", "b", "c", "d"]);
    let left = base.put("a1", 1u32);
    let right = base.put("b1", 1u32);
    assert_eq!(shared_nodes(&left, &right), node_count(&base) - 3, "only the root and the two changed paths differ: c and d are shared");
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 64, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: for any trie and key, a put or remove makes at most `len + 1` new nodes.
    #[test]
    fn s0a_c3_property_changes_copy_only_one_path(keys in proptest::collection::btree_set("[abc]{1,5}", 0..12), key in "[abc]{1,5}") {
        let mut t = Trie::new();
        for k in &keys { t = t.put(k, 1u32); }
        let put = t.put(&key, 2u32);
        prop_assert!(node_count(&put) - shared_nodes(&t, &put) <= key.chars().count() + 1);
        let rem = t.remove(&key);
        prop_assert!(node_count(&rem).saturating_sub(shared_nodes(&t, &rem)) <= key.chars().count() + 1);
        prop_assert!(shared_nodes(&t, &put) <= node_count(&t).min(node_count(&put)));
    }
}
''')))

CH.append(C("0a-c4", M0A, "93-challenge-the-version-that-changed", "debug", "Challenge: the version that changed", "easy", "stages_0a::s0a_c4",
  ["finding the bug where a 'new version' mutates the old one through shared ownership"],
  ["persistent-data-structures-and-path-copying","interior-mutability","property-testing-and-fuzzing"],
  "`src/primer/shared_list.rs` is a small persistent list: `push` returns a **new** list and the old one must stay exactly as it was. It looks right, and after a push the old version has changed. Find the bug and fix it.",
  "Sharing and mutation do not mix: once two values point at the same cell, a write through one is visible through the other. A persistent structure is correct only if no shared node is ever written, which is why Rust's `Arc` gives you no `&mut` and why `Rc<RefCell<..>>` is the wrong tool here even though it compiles.",
  ["`PList::new()`, `push(&self, v) -> PList` (a new version with `v` at the front), `to_vec(&self)` (front first), `len`.","Every version keeps its contents for ever, whatever is pushed onto it or onto its descendants."],
  ["`to_vec` of a version never changes after the version is created.","`push` adds exactly one element at the front."],
  ["`a.push(x).to_vec() == [x] + a.to_vec()`.","Two pushes onto the same version do not see each other.","The length of a version is fixed at creation."],
  ["a = [] ; b = a.push(1) ; c = b.push(2) ; d = b.push(3): b = [1], c = [2,1], d = [3,1]"],
  ["Old versions after a push.","Branching from one version.","A property against a vector model."],
  src=("src/primer/shared_list.rs", '''
//! A persistent singly linked list.

use std::cell::RefCell;
use std::rc::Rc;

struct Node {
    value: i64,
    next: Option<Rc<RefCell<Node>>>,
}

#[derive(Clone)]
pub struct PList {
    head: Option<Rc<RefCell<Node>>>,
    len: usize,
}

impl PList {
    pub fn new() -> PList {
        PList { head: None, len: 0 }
    }

    /// A new list with `v` in front; `self` is unchanged.
    pub fn push(&self, v: i64) -> PList {
        // @begin 0a-c4
        PList { head: Some(Rc::new(RefCell::new(Node { value: v, next: self.head.clone() }))), len: self.len + 1 }
        //~ match &self.head {
        //~     None => PList { head: Some(Rc::new(RefCell::new(Node { value: v, next: None }))), len: 1 },
        //~     Some(h) => {
        //~         // make room at the front by rewriting the head cell: no new cell for `v`
        //~         let rest = Rc::new(RefCell::new(Node { value: h.borrow().value, next: h.borrow().next.clone() }));
        //~         h.borrow_mut().value = v;
        //~         h.borrow_mut().next = Some(rest);
        //~         PList { head: Some(h.clone()), len: self.len + 1 }
        //~     }
        //~ }
        // @end
    }

    pub fn len(&self) -> usize {
        self.len
    }

    pub fn is_empty(&self) -> bool {
        self.len == 0
    }

    pub fn to_vec(&self) -> Vec<i64> {
        let mut out = Vec::with_capacity(self.len);
        let mut cur = self.head.clone();
        while let Some(n) = cur {
            out.push(n.borrow().value);
            cur = n.borrow().next.clone();
        }
        out
    }
}

impl Default for PList {
    fn default() -> Self {
        PList::new()
    }
}
'''),
  test=("tests/stages_0a.rs", '''
use bustub::primer::shared_list::PList;

#[test]
fn s0a_c4_pushing_does_not_change_the_old_version() {
    let a = PList::new();
    let b = a.push(1);
    assert_eq!(a.to_vec(), Vec::<i64>::new());
    assert_eq!(b.to_vec(), vec![1]);
}

#[test]
fn s0a_c4_branching_from_one_version() {
    let b = PList::new().push(1);
    let c = b.push(2);
    let d = b.push(3);
    assert_eq!((b.to_vec(), c.to_vec(), d.to_vec()), (vec![1], vec![2, 1], vec![3, 1]));
}

#[test]
fn s0a_c4_a_version_dropped_and_recreated_does_not_disturb_the_others() {
    let base = PList::new().push(1).push(2);
    {
        let _tmp = base.push(99);
    }
    let after = base.push(7);
    assert_eq!(base.to_vec(), vec![2, 1]);
    assert_eq!(after.to_vec(), vec![7, 2, 1]);
}

#[test]
fn s0a_c4_lengths_are_fixed_at_creation() {
    let a = PList::new().push(5);
    let b = a.push(6);
    assert_eq!((a.len(), b.len()), (1, 2));
    assert!(PList::new().is_empty());
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: a tree of versions, each equal to the vector model of its history, whatever is pushed onto whom.
    #[test]
    fn s0a_c4_property_every_version_keeps_its_contents(ops in proptest::collection::vec((0usize..8, any::<i64>()), 0..30)) {
        let mut versions: Vec<(PList, Vec<i64>)> = vec![(PList::new(), vec![])];
        for (from, v) in ops {
            let (src, model) = versions[from % versions.len()].clone();
            let new = src.push(v);
            let mut m = vec![v];
            m.extend(model);
            versions.push((new, m));
            for (p, m) in &versions {
                prop_assert_eq!(&p.to_vec(), m);
                prop_assert_eq!(p.len(), m.len());
            }
        }
    }
}
''')))

CH.append(C("0a-c5", M0A, "94-challenge-wildcard-keys", "extend", "Challenge: wildcard keys", "medium", "stages_0a::s0a_c5",
  ["searching a trie with a pattern, pruning by the first mismatch","a bounded branching search that never revisits"],
  ["tries","iterators-and-closures"],
  "`keys_matching` in `src/primer/trie_extras.rs`: list the keys of a trie that match a pattern in which `?` matches exactly one character and every other character matches itself. The whole key must match (same length). Written against the public node type of your trie; results in increasing order.",
  "Wildcard search is where a trie beats a hash map: a hash map has to look at every key, while the trie follows only the branches that can still match, so `a?c` visits the `a` subtree and one level below it, not the whole set. The pruning is the exercise.",
  ["`keys_matching(trie, pattern) -> Vec<String>`; `?` is one character, anything else a literal.","A key matches when it has the same number of characters as the pattern and each position agrees (or the pattern has `?` there).","The trie is only read."],
  ["Every result has a value in the trie and the pattern's length.","Results are sorted and unique."],
  ["A pattern without `?` returns at most the key itself.","Replacing a letter of a pattern by `?` can only add results.","`keys_matching` of `?` repeated `n` times lists exactly the keys of length `n`."],
  ["keys {abc, abd, aec, xyz}: \"a?c\" -> [abc, aec]; \"ab?\" -> [abc, abd]; \"???\" -> all four"],
  ["Literals, wildcards, lengths.","Empty pattern and the empty key.","A property against filtering the key list."],
  src=("src/primer/trie_extras.rs", '''
//! Extra queries over your persistent trie, written against its public node type only.

use std::sync::Arc;

use crate::primer::trie::{Trie, TrieNode};

/// Every key in `trie` that starts with `prefix`, in increasing order.
pub fn keys_with_prefix(trie: &Trie, prefix: &str) -> Vec<String> {
    // @begin 0a-c2
    fn walk(node: &Arc<TrieNode>, path: &mut String, out: &mut Vec<String>) {
        if node.value.is_some() {
            out.push(path.clone());
        }
        for (c, child) in &node.children {
            path.push(*c);
            walk(child, path, out);
            path.pop();
        }
    }
    let Some(mut node) = trie.root() else { return Vec::new() };
    for c in prefix.chars() {
        match node.children.get(&c) {
            Some(child) => node = child,
            None => return Vec::new(),
        }
    }
    let mut out = Vec::new();
    walk(node, &mut prefix.to_owned(), &mut out);
    out
    //~ todo!("0a-c2: follow the prefix down, then collect every value below, children in order")
    // @end
}

fn count(node: &Arc<TrieNode>) -> usize {
    // @begin 0a-c3
    1 + node.children.values().map(count).sum::<usize>()
    //~ todo!("0a-c3: this node and everything below it")
    // @end
}

/// The number of nodes of the trie.
pub fn node_count(trie: &Trie) -> usize {
    // @begin 0a-c3
    trie.root().map_or(0, count)
    //~ todo!("0a-c3: nodes reachable from the root")
    // @end
}

fn shared(a: &Arc<TrieNode>, b: &Arc<TrieNode>) -> usize {
    // @begin 0a-c3
    if Arc::ptr_eq(a, b) {
        return count(a);
    }
    a.children.iter().map(|(c, ca)| b.children.get(c).map_or(0, |cb| shared(ca, cb))).sum()
    //~ todo!("0a-c3: a node that is the same allocation shares its whole subtree; otherwise compare the children with the same letter")
    // @end
}

/// How many nodes the two tries have in common (the same allocation at the same path).
pub fn shared_nodes(a: &Trie, b: &Trie) -> usize {
    // @begin 0a-c3
    match (a.root(), b.root()) {
        (Some(x), Some(y)) => shared(x, y),
        _ => 0,
    }
    //~ todo!("0a-c3: walk both tries together")
    // @end
}

/// The keys of `trie` that match `pattern` (`?` is any one character), in increasing order.
pub fn keys_matching(trie: &Trie, pattern: &str) -> Vec<String> {
    // @begin 0a-c5
    fn go(node: &Arc<TrieNode>, pat: &[char], path: &mut String, out: &mut Vec<String>) {
        match pat.split_first() {
            None => {
                if node.value.is_some() {
                    out.push(path.clone());
                }
            }
            Some((&'?', rest)) => {
                for (c, child) in &node.children {
                    path.push(*c);
                    go(child, rest, path, out);
                    path.pop();
                }
            }
            Some((c, rest)) => {
                if let Some(child) = node.children.get(c) {
                    path.push(*c);
                    go(child, rest, path, out);
                    path.pop();
                }
            }
        }
    }
    let pat: Vec<char> = pattern.chars().collect();
    let mut out = Vec::new();
    if let Some(root) = trie.root() {
        go(root, &pat, &mut String::new(), &mut out);
    }
    out
    //~ todo!("0a-c5: descend letter by letter; a ? tries every child, a literal only its own")
    // @end
}
'''),
  test=("tests/stages_0a.rs", '''
use bustub::primer::trie::Trie;
use bustub::primer::trie_extras::keys_matching;

fn build(keys: &[&str]) -> Trie {
    keys.iter().fold(Trie::new(), |t, k| t.put(k, 1u32))
}

#[test]
fn s0a_c5_a_question_mark_matches_exactly_one_character() {
    let t = build(&["abc", "abd", "aec", "xyz"]);
    assert_eq!(keys_matching(&t, "a?c"), vec!["abc", "aec"]);
    assert_eq!(keys_matching(&t, "ab?"), vec!["abc", "abd"]);
    assert_eq!(keys_matching(&t, "???"), vec!["abc", "abd", "aec", "xyz"]);
}

#[test]
fn s0a_c5_the_length_must_match() {
    let t = build(&["a", "ab", "abc"]);
    assert_eq!(keys_matching(&t, "a?"), vec!["ab"]);
    assert_eq!(keys_matching(&t, "?"), vec!["a"]);
    assert_eq!(keys_matching(&t, "????"), Vec::<String>::new());
}

#[test]
fn s0a_c5_literals_only_and_the_empty_pattern() {
    let t = build(&["", "a", "ab"]);
    assert_eq!(keys_matching(&t, "ab"), vec!["ab"]);
    assert_eq!(keys_matching(&t, ""), vec![""], "the empty key matches the empty pattern");
    assert_eq!(keys_matching(&Trie::new(), "?"), Vec::<String>::new());
}

#[test]
fn s0a_c5_results_come_back_in_key_order() {
    let t = build(&["ac", "ab", "bb", "aa"]);
    assert_eq!(keys_matching(&t, "a?"), vec!["aa", "ab", "ac"]);
    assert_eq!(keys_matching(&t, "?b"), vec!["ab", "bb"]);
}

#[test]
fn s0a_c5_results_come_back_in_key_order() {
    let t = build(&["ac", "ab", "bb", "aa"]);
    assert_eq!(keys_matching(&t, "a?"), vec!["aa", "ab", "ac"]);
    assert_eq!(keys_matching(&t, "?b"), vec!["ab", "bb"]);
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: equals filtering the key set by a position-by-position match.
    #[test]
    fn s0a_c5_property_matching_equals_a_filter(keys in proptest::collection::btree_set("[abc]{0,4}", 0..12), pattern in "[abc?]{0,4}") {
        let mut t = Trie::new();
        for k in &keys { t = t.put(k, 1u32); }
        let m = |k: &str| k.chars().count() == pattern.chars().count() && k.chars().zip(pattern.chars()).all(|(a, p)| p == '?' || a == p);
        let want: Vec<String> = keys.iter().filter(|k| m(k)).cloned().collect();
        prop_assert_eq!(keys_matching(&t, &pattern), want);
    }
}
''')))

CH.append(C("0b-c1", M0B, "90-challenge-a-geometric-level-generator", "build", "Challenge: a level generator", "easy", "stages_0b::s0b_c1",
  ["drawing a skip-list height from coin flips with a given probability","a seeded generator so that tests are reproducible"],
  ["skip-lists","property-testing-and-fuzzing"],
  "`LevelGenerator` in `src/primer/level_gen.rs`: the height draw of a skip list, on its own. `next_level()` returns `1 + (the number of consecutive successes)` where each trial succeeds with probability `1 / branching` (`branching` of 2 is a fair coin, 4 is what BusTub uses), never more than `max_level`. Driven by a seeded xorshift generator (given), so a seed always gives the same sequence.",
  "A skip list is balanced by chance, and the *distribution* of heights is what makes it fast: half the nodes only at the bottom, a quarter one level up, and so on. A generator that is off by one level (taller towers, or never reaching the cap) leaves the list correct and slow, and nothing but a statistical test shows it.",
  ["`LevelGenerator::new(seed, branching, max_level)`; `branching >= 2`, `max_level >= 1`.","`next_level()` is in `1..=max_level`. It makes trials until one fails or `max_level` is reached; each trial succeeds when the next random value is divisible by `branching`.","The same seed gives the same sequence."],
  ["Every level is between 1 and `max_level`.","The generator is deterministic given its seed."],
  ["About `1 / branching` of the draws are at least 2, about `1 / branching^2` at least 3.","With `max_level = 1` every draw is 1.","Two generators with the same seed produce the same draws; different seeds almost always differ."],
  ["max_level 1 -> always 1","branching 2, 20 000 draws: about 10 000 are >= 2"],
  ["The bounds and determinism.","The tail of the distribution over many draws.","A property over seeds and parameters."],
  src=("src/primer/level_gen.rs", '''
//! The random height of a skip-list node.

/// A small seeded xorshift generator (given).
pub struct XorShift(u64);

impl XorShift {
    pub fn new(seed: u64) -> XorShift {
        XorShift(seed.max(1))
    }

    pub fn next_u64(&mut self) -> u64 {
        let mut x = self.0;
        x ^= x << 13;
        x ^= x >> 7;
        x ^= x << 17;
        self.0 = x;
        x
    }
}

pub struct LevelGenerator {
    // @begin 0b-c1
    rng: XorShift,
    branching: u64,
    max_level: usize,
    //~ _gen: (),
    // @end
}

impl LevelGenerator {
    pub fn new(seed: u64, branching: u64, max_level: usize) -> LevelGenerator {
        // @begin 0b-c1
        LevelGenerator { rng: XorShift::new(seed), branching: branching.max(2), max_level: max_level.max(1) }
        //~ todo!("0b-c1: remember the generator and the limits")
        // @end
    }

    /// A level in `1..=max_level`.
    pub fn next_level(&mut self) -> usize {
        // @begin 0b-c1
        let mut level = 1;
        while level < self.max_level && self.rng.next_u64() % self.branching == 0 {
            level += 1;
        }
        level
        //~ todo!("0b-c1: 1, plus one for every trial that succeeds, up to the maximum")
        // @end
    }
}
'''),
  test=("tests/stages_0b.rs", '''
use bustub::primer::level_gen::LevelGenerator;

#[test]
fn s0b_c1_levels_stay_within_one_and_the_maximum() {
    let mut g = LevelGenerator::new(7, 2, 5);
    for _ in 0..5000 {
        let l = g.next_level();
        assert!((1..=5).contains(&l), "level {l}");
    }
}

#[test]
fn s0b_c1_a_maximum_of_one_is_always_one() {
    let mut g = LevelGenerator::new(1, 2, 1);
    assert!((0..100).all(|_| g.next_level() == 1));
}

#[test]
fn s0b_c1_the_same_seed_gives_the_same_sequence() {
    let a: Vec<_> = { let mut g = LevelGenerator::new(42, 4, 14); (0..200).map(|_| g.next_level()).collect() };
    let b: Vec<_> = { let mut g = LevelGenerator::new(42, 4, 14); (0..200).map(|_| g.next_level()).collect() };
    let c: Vec<_> = { let mut g = LevelGenerator::new(43, 4, 14); (0..200).map(|_| g.next_level()).collect() };
    assert_eq!(a, b);
    assert_ne!(a, c);
}

#[test]
fn s0b_c1_the_tail_of_the_distribution_is_geometric() {
    for (branching, expected) in [(2u64, 0.5f64), (4, 0.25)] {
        let mut g = LevelGenerator::new(12345, branching, 20);
        let n = 40_000;
        let (mut ge2, mut ge3) = (0, 0);
        for _ in 0..n {
            let l = g.next_level();
            ge2 += usize::from(l >= 2);
            ge3 += usize::from(l >= 3);
        }
        let (p2, p3) = (ge2 as f64 / n as f64, ge3 as f64 / n as f64);
        assert!((p2 - expected).abs() < 0.02, "branching {branching}: P(level >= 2) = {p2}, expected {expected}");
        assert!((p3 - expected * expected).abs() < 0.02, "branching {branching}: P(level >= 3) = {p3}, expected {}", expected * expected);
    }
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 64, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: always within bounds, for any seed and parameters.
    #[test]
    fn s0b_c1_property_bounds_hold_for_any_seed(seed in any::<u64>(), branching in 2u64..9, max in 1usize..16) {
        let mut g = LevelGenerator::new(seed, branching, max);
        for _ in 0..200 { let l = g.next_level(); prop_assert!(l >= 1 && l <= max); }
    }
}
''')))

CH.append(C("0b-c2", M0B, "91-challenge-an-integrity-checker", "extend", "Challenge: an integrity checker", "medium", "stages_0b::s0b_c2",
  ["stating the invariants of a skip list as code","using a checker to test an implementation over many operations"],
  ["skip-lists","checking-invariants","property-testing-and-fuzzing"],
  "`check_integrity` in `src/primer/skiplist_extras.rs`: given **your** `SkipList<i32>`, verify its structural invariants through its public view (`nodes()` for the keys with their heights, `level(l)` for the keys linked at level `l`) and return the first violation found. Then a test drives your list with thousands of random inserts and erases and runs the checker after every one.",
  "The point of an invariant checker is that it makes every later bug local: a skip list that loses a key at level 3 passes small hand-written tests and fails once in ten thousand operations. A checker that runs after each operation turns that failure into the exact operation that caused it. Writing it also forces you to say what \"a correct skip list\" means.",
  ["Level 0 holds every key, strictly increasing, and `size()` equals its length.","For every level `l >= 1`, `level(l)` is strictly increasing and a **subsequence** of `level(l - 1)`.","The height of each node in `nodes()` equals the number of levels in which its key appears (and is at least 1).","`check_integrity(list) -> Result<(), String>`; the message names the level and the key."],
  ["A correctly implemented list always passes after any sequence of operations.","The checker reads only; it never changes the list."],
  ["Removing a key from the middle of one level of a good list makes the checker fail (tested on a corrupted copy of the data).","The checker agrees with `nodes()` and `level()` on an empty list.","Passing after every step of a random workload means every intermediate state was valid."],
  ["list {1, 2, 3} with heights {1, 3, 2}: level 1 = [2, 3]; level 2 = [2]"],
  ["Small lists; the empty list.","Corrupted level data is rejected (the checker works on the views, so the tests feed it constructed views).","A random workload against your list."],
  src=("src/primer/skiplist_extras.rs", '''
//! Extras over your skip list, written against its public view.

use crate::primer::skiplist::SkipList;

/// The views `check_levels` works on: for every level, the keys linked there; the (key, height) list of level 0; the size.
pub fn check_levels(levels: &[Vec<i32>], nodes: &[(i32, usize)], size: usize) -> Result<(), String> {
    // @begin 0b-c2
    let Some(bottom) = levels.first() else {
        return if size == 0 && nodes.is_empty() { Ok(()) } else { Err("no levels but the list is not empty".into()) };
    };
    if bottom.len() != size || nodes.len() != size {
        return Err(format!("level 0 has {} keys, nodes() has {}, size() is {size}", bottom.len(), nodes.len()));
    }
    for (l, keys) in levels.iter().enumerate() {
        if let Some(w) = keys.windows(2).find(|w| w[0] >= w[1]) {
            return Err(format!("level {l} is not strictly increasing at {} then {}", w[0], w[1]));
        }
        if l > 0 {
            let below = &levels[l - 1];
            let mut it = below.iter();
            for k in keys {
                if !it.any(|b| b == k) {
                    return Err(format!("key {k} is on level {l} but not (in order) on level {}", l - 1));
                }
            }
        }
    }
    for (k, h) in nodes {
        let appears = levels.iter().filter(|lv| lv.contains(k)).count();
        if *h < 1 || *h != appears {
            return Err(format!("key {k} has height {h} but appears on {appears} levels"));
        }
    }
    Ok(())
    //~ todo!("0b-c2: level 0 holds every key in order; each higher level is an ordered subsequence of the one below; heights match the number of levels a key is on")
    // @end
}

/// Checks `list` through its public view.
pub fn check_integrity(list: &SkipList<i32>) -> Result<(), String> {
    // @begin 0b-c2
    let nodes = list.nodes();
    let top = nodes.iter().map(|n| n.1).max().unwrap_or(0);
    let levels: Vec<Vec<i32>> = (0..top).map(|l| list.level(l)).collect();
    check_levels(&levels, &nodes, list.size())
    //~ todo!("0b-c2: collect the levels from the list and check them")
    // @end
}
'''),
  test=("tests/stages_0b.rs", '''
use bustub::primer::skiplist::SkipList;
use bustub::primer::skiplist_extras::{check_integrity, check_levels};

#[test]
fn s0b_c2_a_well_formed_view_passes() {
    let levels = vec![vec![1, 2, 3], vec![2, 3], vec![2]];
    let nodes = vec![(1, 1), (2, 3), (3, 2)];
    assert_eq!(check_levels(&levels, &nodes, 3), Ok(()));
    assert_eq!(check_levels(&[], &[], 0), Ok(()));
}

#[test]
fn s0b_c2_a_key_on_a_higher_level_but_not_below_is_rejected() {
    let levels = vec![vec![1, 3], vec![2]];
    assert!(check_levels(&levels, &[(1, 1), (3, 1)], 2).is_err());
}

#[test]
fn s0b_c2_a_level_that_is_not_sorted_or_has_repeats_is_rejected() {
    assert!(check_levels(&[vec![2, 1]], &[(2, 1), (1, 1)], 2).is_err());
    assert!(check_levels(&[vec![1, 1]], &[(1, 1), (1, 1)], 2).is_err());
}

#[test]
fn s0b_c2_a_wrong_height_or_size_is_rejected() {
    let levels = vec![vec![1, 2], vec![2]];
    assert!(check_levels(&levels, &[(1, 1), (2, 1)], 2).is_err(), "key 2 appears on two levels but claims height 1");
    assert!(check_levels(&levels, &[(1, 1), (2, 2)], 3).is_err(), "size 3 but two keys");
    assert!(check_levels(&[], &[(1, 1)], 0).is_err());
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 32, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: your skip list passes the checker after every operation of a random workload, and holds exactly the keys of a `BTreeSet`.
    #[test]
    fn s0b_c2_property_your_list_stays_valid(ops in proptest::collection::vec((any::<bool>(), 0i32..40), 0..150)) {
        let list: SkipList<i32> = SkipList::new();
        let mut model = std::collections::BTreeSet::new();
        for (insert, k) in ops {
            if insert { prop_assert_eq!(list.insert(&k), model.insert(k)); } else { prop_assert_eq!(list.erase(&k), model.remove(&k)); }
            prop_assert_eq!(check_integrity(&list), Ok(()), "after {} {}", if insert { "insert" } else { "erase" }, k);
            prop_assert_eq!(list.size(), model.len());
        }
        prop_assert_eq!(list.level(0), model.iter().copied().collect::<Vec<_>>());
    }
}
''')))

CH.append(C("0b-c3", M0B, "92-challenge-counting-a-range", "extend", "Challenge: counting a range", "easy", "stages_0b::s0b_c3",
  ["answering a range query through the bottom level of an ordered structure","where a plain skip list stops and an indexable one begins"],
  ["skip-lists","ordered-sets-as-priority-queues"],
  "`range_count` and `floor` in `src/primer/skiplist_extras.rs`: using only the public view of **your** `SkipList<i32>` (`level(0)` is every key in order), `range_count(list, lo, hi)` counts the keys in `lo..=hi` and `floor(list, k)` returns the largest key `<= k`.",
  "`BETWEEN`, `ORDER BY ... LIMIT` and predecessor queries are what ordered structures are *for*. A skip list can answer them by descending to the start and walking; with only the public view you get the same answers by binary search on the bottom level. Seeing the difference between what the structure *can* do fast (a descent) and what the interface lets you do (a walk) is the lesson.",
  ["`range_count(list, lo, hi)`: the number of keys `k` with `lo <= k <= hi` (0 if `hi < lo`).","`floor(list, k)`: the largest stored key `<= k`, or `None`."],
  ["The results depend only on the keys stored, not on their heights.","Both read only."],
  ["`range_count(l, a, b) == range_count(l, a, m) + range_count(l, m + 1, b)` for `a <= m < b`.","`floor(l, k)` is in the list when it exists, and no key lies strictly between it and `k`.","Inserting a key inside the range raises the count by one."],
  ["keys {10, 20, 30}: range_count(15, 30) = 2; floor(25) = 20; floor(5) = None"],
  ["Counting and floor on a small list.","Empty ranges and the empty list.","A property against a `BTreeSet`."],
  src=("src/primer/skiplist_extras.rs", '''
//! Extras over your skip list, written against its public view.

use crate::primer::skiplist::SkipList;

/// The views `check_levels` works on: for every level, the keys linked there; the (key, height) list of level 0; the size.
pub fn check_levels(levels: &[Vec<i32>], nodes: &[(i32, usize)], size: usize) -> Result<(), String> {
    // @begin 0b-c2
    let Some(bottom) = levels.first() else {
        return if size == 0 && nodes.is_empty() { Ok(()) } else { Err("no levels but the list is not empty".into()) };
    };
    if bottom.len() != size || nodes.len() != size {
        return Err(format!("level 0 has {} keys, nodes() has {}, size() is {size}", bottom.len(), nodes.len()));
    }
    for (l, keys) in levels.iter().enumerate() {
        if let Some(w) = keys.windows(2).find(|w| w[0] >= w[1]) {
            return Err(format!("level {l} is not strictly increasing at {} then {}", w[0], w[1]));
        }
        if l > 0 {
            let below = &levels[l - 1];
            let mut it = below.iter();
            for k in keys {
                if !it.any(|b| b == k) {
                    return Err(format!("key {k} is on level {l} but not (in order) on level {}", l - 1));
                }
            }
        }
    }
    for (k, h) in nodes {
        let appears = levels.iter().filter(|lv| lv.contains(k)).count();
        if *h < 1 || *h != appears {
            return Err(format!("key {k} has height {h} but appears on {appears} levels"));
        }
    }
    Ok(())
    //~ todo!("0b-c2: level 0 holds every key in order; each higher level is an ordered subsequence of the one below; heights match the number of levels a key is on")
    // @end
}

/// Checks `list` through its public view.
pub fn check_integrity(list: &SkipList<i32>) -> Result<(), String> {
    // @begin 0b-c2
    let nodes = list.nodes();
    let top = nodes.iter().map(|n| n.1).max().unwrap_or(0);
    let levels: Vec<Vec<i32>> = (0..top).map(|l| list.level(l)).collect();
    check_levels(&levels, &nodes, list.size())
    //~ todo!("0b-c2: collect the levels from the list and check them")
    // @end
}

/// How many keys `k` satisfy `lo <= k <= hi`.
pub fn range_count(list: &SkipList<i32>, lo: i32, hi: i32) -> usize {
    // @begin 0b-c3
    if hi < lo {
        return 0;
    }
    let keys = list.level(0);
    keys.partition_point(|&k| k <= hi) - keys.partition_point(|&k| k < lo)
    //~ todo!("0b-c3: binary search both ends of the sorted bottom level")
    // @end
}

/// The largest key `<= k`.
pub fn floor(list: &SkipList<i32>, k: i32) -> Option<i32> {
    // @begin 0b-c3
    let keys = list.level(0);
    let at = keys.partition_point(|&x| x <= k);
    at.checked_sub(1).map(|i| keys[i])
    //~ todo!("0b-c3: the last key not above k")
    // @end
}
'''),
  test=("tests/stages_0b.rs", '''
use bustub::primer::skiplist::SkipList;
use bustub::primer::skiplist_extras::{floor, range_count};
use std::collections::BTreeSet;

fn list_of(keys: &[i32]) -> SkipList<i32> {
    let l = SkipList::new();
    for k in keys {
        l.insert(k);
    }
    l
}

#[test]
fn s0b_c3_range_counts_include_both_ends() {
    let l = list_of(&[10, 20, 30]);
    assert_eq!(range_count(&l, 15, 30), 2);
    assert_eq!(range_count(&l, 10, 10), 1);
    assert_eq!(range_count(&l, 0, 100), 3);
    assert_eq!(range_count(&l, 21, 29), 0);
}

#[test]
fn s0b_c3_reversed_ranges_and_the_empty_list() {
    assert_eq!(range_count(&list_of(&[1, 2, 3]), 3, 1), 0);
    assert_eq!(range_count(&list_of(&[]), 0, 10), 0);
}

#[test]
fn s0b_c3_floor_is_the_largest_key_not_above() {
    let l = list_of(&[10, 20, 30]);
    assert_eq!((floor(&l, 25), floor(&l, 20), floor(&l, 5), floor(&l, 99)), (Some(20), Some(20), None, Some(30)));
    assert_eq!(floor(&list_of(&[]), 1), None);
}

#[test]
fn s0b_c3_negative_keys_and_a_key_inserted_twice() {
    let l = list_of(&[-5, -5, 0, 5]);
    assert_eq!(range_count(&l, -10, -1), 1);
    assert_eq!((floor(&l, -5), floor(&l, -6)), (Some(-5), None));
}

#[test]
fn s0b_c3_negative_keys_and_a_key_inserted_twice() {
    let l = list_of(&[-5, -5, 0, 5]);
    assert_eq!(range_count(&l, -10, -1), 1);
    assert_eq!((floor(&l, -5), floor(&l, -6)), (Some(-5), None));
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 64, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: against a `BTreeSet`.
    #[test]
    fn s0b_c3_property_counts_and_floors_match_a_set(keys in proptest::collection::btree_set(-20i32..20, 0..15), lo in -25i32..25, hi in -25i32..25, k in -25i32..25) {
        let l = list_of(&keys.iter().copied().collect::<Vec<_>>());
        prop_assert_eq!(range_count(&l, lo, hi), if hi < lo { 0 } else { keys.range(lo..=hi).count() });
        prop_assert_eq!(floor(&l, k), keys.range(..=k).next_back().copied());
    }
}
''')))

CH.append(C("0b-c4", M0B, "93-challenge-one-level-too-tall", "debug", "Challenge: one level too tall", "easy", "stages_0b::s0b_c4",
  ["finding an off-by-one in a loop bound that only shows when the maximum is reached"],
  ["skip-lists","property-testing-and-fuzzing"],
  "`random_height` in `src/primer/height.rs` draws a node's height from a source of coin flips and must never exceed `max`. It works in nearly every run, and once in a while it returns `max + 1` (and a list built on it indexes past its tower array). Find the bug and fix it.",
  "The loop `while flip() { level += 1 }` is half the code of a skip list and the half most often written without its bound: with the bound on the wrong side of the comparison, the failure waits for `max` consecutive heads, which at 14 levels and a fair coin is once in sixteen thousand nodes. A test that controls the coin makes it a certainty.",
  ["`random_height(flip, max)`: start at 1; while `flip()` returns true **and** the height is below `max`, add one. The result is in `1..=max`.","`flip` is called at most `max` times, and not at all when `max == 1`."],
  ["The height is never above `max`.","The height is `1 + the number of leading heads`, capped at `max`."],
  ["With a coin that is always heads the result is exactly `max`.","With a coin that is always tails the result is 1 and `flip` was called once.","`flip` is never called after the cap is reached."],
  ["max 4, always heads -> 4","max 4, H H T -> 3","max 1, any coin -> 1 with no flips"],
  ["Always heads, always tails and mixed sequences.","The number of flips.","A property over all coin sequences."],
  src=("src/primer/height.rs", '''
//! The random height of a skip-list node, from a source of coin flips.

pub fn random_height(mut flip: impl FnMut() -> bool, max: usize) -> usize {
    let mut level = 1;
    // @begin 0b-c4
    while level < max && flip() {
        level += 1;
    }
    //~ while flip() && level <= max {
    //~     level += 1;
    //~ }
    // @end
    level
}
'''),
  test=("tests/stages_0b.rs", '''
use bustub::primer::height::random_height;

fn coin(seq: &[bool]) -> impl FnMut() -> bool + '_ {
    let mut i = 0;
    move || {
        let v = seq.get(i).copied().unwrap_or(false);
        i += 1;
        v
    }
}

#[test]
fn s0b_c4_a_coin_that_is_always_heads_stops_at_the_maximum() {
    let mut flips = 0;
    let h = random_height(|| { flips += 1; true }, 4);
    assert_eq!(h, 4);
    assert_eq!(flips, 3, "three flips take the height from 1 to 4; none after the cap");
}

#[test]
fn s0b_c4_tails_ends_the_climb() {
    assert_eq!(random_height(coin(&[true, true, false]), 8), 3);
    assert_eq!(random_height(coin(&[false]), 8), 1);
}

#[test]
fn s0b_c4_a_maximum_of_one_never_flips() {
    let mut flips = 0;
    assert_eq!(random_height(|| { flips += 1; true }, 1), 1);
    assert_eq!(flips, 0);
}

#[test]
fn s0b_c4_each_level_climbed_costs_one_flip() {
    for heads in 0..6 {
        let mut seq = vec![true; heads];
        seq.push(false);
        let mut flips = 0;
        let h = random_height(|| { let v = seq[flips]; flips += 1; v }, 10);
        assert_eq!((h, flips), (heads + 1, heads + 1));
    }
}

#[test]
fn s0b_c4_each_level_climbed_costs_one_flip() {
    for heads in 0..6 {
        let mut seq = vec![true; heads];
        seq.push(false);
        let mut flips = 0;
        let h = random_height(|| { let v = seq[flips]; flips += 1; v }, 10);
        assert_eq!((h, flips), (heads + 1, heads + 1));
    }
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: `1 + leading heads`, capped at the maximum, for any sequence of flips.
    #[test]
    fn s0b_c4_property_the_height_is_leading_heads_capped(seq in proptest::collection::vec(any::<bool>(), 0..24), max in 1usize..16) {
        let heads = seq.iter().take_while(|&&b| b).count();
        let want = (1 + heads).min(max);
        let mut flips = 0;
        let got = random_height(|| { let v = seq.get(flips).copied().unwrap_or(false); flips += 1; v }, max);
        prop_assert_eq!(got, want);
        prop_assert!(flips <= max);
    }
}
''')))

CH.append(C("0b-c5", M0B, "94-challenge-the-union-of-two-lists", "extend", "Challenge: the union of two lists", "easy", "stages_0b::s0b_c5",
  ["building one ordered structure from two using only the public operations","what the cost of a merge depends on"],
  ["skip-lists","ordered-sets-as-priority-queues"],
  "`union` in `src/primer/skiplist_extras.rs`: build a **new** `SkipList<i32>` holding every key of two lists (`a` and `b` are left untouched), using your list's public `insert` and `level(0)`. A key in both appears once.",
  "Set union is the simplest compound operation on ordered sets and the one every merge, replication catch-up and index rebuild depends on. With only `insert` available it costs `O((n + m) log (n + m))`; knowing that a sorted merge would be `O(n + m)` and why a skip list built by repeated insert cannot use it is part of choosing a structure.",
  ["`union(a, b)` returns a new list whose keys are the set union; sizes add up minus the common keys.","`a` and `b` are not modified."],
  ["The result's `level(0)` is strictly increasing and equals the union of the keys.","The result passes the structure's own invariants (heights between 1 and the maximum)."],
  ["`union(a, b)` has the same keys as `union(b, a)`.","`union(a, a)` has the keys of `a`.","`union(a, empty)` has the keys of `a`."],
  ["a {1, 3, 5}, b {3, 4}: union {1, 3, 4, 5}"],
  ["Small unions, empty inputs.","Inputs are untouched.","A property against `BTreeSet`."],
  src=("src/primer/skiplist_extras.rs", '''
//! Extras over your skip list, written against its public view.

use crate::primer::skiplist::SkipList;

/// The views `check_levels` works on: for every level, the keys linked there; the (key, height) list of level 0; the size.
pub fn check_levels(levels: &[Vec<i32>], nodes: &[(i32, usize)], size: usize) -> Result<(), String> {
    // @begin 0b-c2
    let Some(bottom) = levels.first() else {
        return if size == 0 && nodes.is_empty() { Ok(()) } else { Err("no levels but the list is not empty".into()) };
    };
    if bottom.len() != size || nodes.len() != size {
        return Err(format!("level 0 has {} keys, nodes() has {}, size() is {size}", bottom.len(), nodes.len()));
    }
    for (l, keys) in levels.iter().enumerate() {
        if let Some(w) = keys.windows(2).find(|w| w[0] >= w[1]) {
            return Err(format!("level {l} is not strictly increasing at {} then {}", w[0], w[1]));
        }
        if l > 0 {
            let below = &levels[l - 1];
            let mut it = below.iter();
            for k in keys {
                if !it.any(|b| b == k) {
                    return Err(format!("key {k} is on level {l} but not (in order) on level {}", l - 1));
                }
            }
        }
    }
    for (k, h) in nodes {
        let appears = levels.iter().filter(|lv| lv.contains(k)).count();
        if *h < 1 || *h != appears {
            return Err(format!("key {k} has height {h} but appears on {appears} levels"));
        }
    }
    Ok(())
    //~ todo!("0b-c2: level 0 holds every key in order; each higher level is an ordered subsequence of the one below; heights match the number of levels a key is on")
    // @end
}

/// Checks `list` through its public view.
pub fn check_integrity(list: &SkipList<i32>) -> Result<(), String> {
    // @begin 0b-c2
    let nodes = list.nodes();
    let top = nodes.iter().map(|n| n.1).max().unwrap_or(0);
    let levels: Vec<Vec<i32>> = (0..top).map(|l| list.level(l)).collect();
    check_levels(&levels, &nodes, list.size())
    //~ todo!("0b-c2: collect the levels from the list and check them")
    // @end
}

/// How many keys `k` satisfy `lo <= k <= hi`.
pub fn range_count(list: &SkipList<i32>, lo: i32, hi: i32) -> usize {
    // @begin 0b-c3
    if hi < lo {
        return 0;
    }
    let keys = list.level(0);
    keys.partition_point(|&k| k <= hi) - keys.partition_point(|&k| k < lo)
    //~ todo!("0b-c3: binary search both ends of the sorted bottom level")
    // @end
}

/// The largest key `<= k`.
pub fn floor(list: &SkipList<i32>, k: i32) -> Option<i32> {
    // @begin 0b-c3
    let keys = list.level(0);
    let at = keys.partition_point(|&x| x <= k);
    at.checked_sub(1).map(|i| keys[i])
    //~ todo!("0b-c3: the last key not above k")
    // @end
}

/// A new list with every key of `a` and of `b`.
pub fn union(a: &SkipList<i32>, b: &SkipList<i32>) -> SkipList<i32> {
    // @begin 0b-c5
    let out = SkipList::new();
    for k in a.level(0).into_iter().chain(b.level(0)) {
        out.insert(&k);
    }
    out
    //~ todo!("0b-c5: insert every key of both lists into a new list")
    // @end
}
'''),
  test=("tests/stages_0b.rs", '''
use bustub::primer::skiplist::SkipList;
use bustub::primer::skiplist_extras::{check_integrity, union};
use std::collections::BTreeSet;

fn list_of(keys: &[i32]) -> SkipList<i32> {
    let l = SkipList::new();
    for k in keys {
        l.insert(k);
    }
    l
}

#[test]
fn s0b_c5_a_key_in_both_lists_appears_once() {
    let u = union(&list_of(&[1, 3, 5]), &list_of(&[3, 4]));
    assert_eq!(u.level(0), vec![1, 3, 4, 5]);
    assert_eq!(u.size(), 4);
}

#[test]
fn s0b_c5_the_inputs_are_left_alone() {
    let (a, b) = (list_of(&[1, 2]), list_of(&[2, 3]));
    let _ = union(&a, &b);
    assert_eq!((a.level(0), b.level(0)), (vec![1, 2], vec![2, 3]));
}

#[test]
fn s0b_c5_empty_inputs() {
    assert_eq!(union(&list_of(&[]), &list_of(&[])).size(), 0);
    assert_eq!(union(&list_of(&[7]), &list_of(&[])).level(0), vec![7]);
    assert_eq!(union(&list_of(&[]), &list_of(&[7])).level(0), vec![7]);
}

#[test]
fn s0b_c5_the_union_is_a_valid_list_you_can_keep_using() {
    let u = union(&list_of(&[2, 4]), &list_of(&[1, 4, 6]));
    assert_eq!(check_integrity(&u), Ok(()));
    assert!(u.insert(&3));
    assert!(!u.insert(&4), "4 is already there");
    assert_eq!(u.level(0), vec![1, 2, 3, 4, 6]);
}

#[test]
fn s0b_c5_the_union_is_a_valid_list_you_can_keep_using() {
    let u = union(&list_of(&[2, 4]), &list_of(&[1, 4, 6]));
    assert_eq!(check_integrity(&u), Ok(()));
    assert!(u.insert(&3));
    assert!(!u.insert(&4), "4 is already there");
    assert_eq!(u.level(0), vec![1, 2, 3, 4, 6]);
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 64, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: the union of two sets, a valid list, and symmetric.
    #[test]
    fn s0b_c5_property_union_is_a_set_union(a in proptest::collection::btree_set(0i32..30, 0..12), b in proptest::collection::btree_set(0i32..30, 0..12)) {
        let (la, lb) = (list_of(&a.iter().copied().collect::<Vec<_>>()), list_of(&b.iter().copied().collect::<Vec<_>>()));
        let u = union(&la, &lb);
        let want: Vec<i32> = a.union(&b).copied().collect::<BTreeSet<_>>().into_iter().collect();
        prop_assert_eq!(u.level(0), want.clone());
        prop_assert_eq!(union(&lb, &la).level(0), want);
        prop_assert_eq!(check_integrity(&u), Ok(()));
    }
}
''')))
