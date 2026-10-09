//! Tests for module 0a: a persistent trie and a thread-safe store over it.

use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;

use std::collections::BTreeMap;

use bustub::primer::trie::{Trie, TrieNode};
use bustub::primer::trie_store::TrieStore;

fn t() -> Trie {
    Trie::new()
}

// ---- 0a-01: get ---------------------------------------------------------------------------------------------------------------------------
//
// Stage 1 comes before `put`, so these tests build their tries by hand from the (given) public fields of `TrieNode`.

fn value_node<T: std::any::Any + Send + Sync>(children: Vec<(char, Arc<TrieNode>)>, value: T) -> Arc<TrieNode> {
    Arc::new(TrieNode { children: children.into_iter().collect::<BTreeMap<_, _>>(), value: Some(Arc::new(value)) })
}

fn plain_node(children: Vec<(char, Arc<TrieNode>)>) -> Arc<TrieNode> {
    Arc::new(TrieNode { children: children.into_iter().collect::<BTreeMap<_, _>>(), value: None })
}

/// A trie with the single key "test" holding `233u32`: root, t, e, s, t(value).
fn test_trie() -> Trie {
    let leaf = value_node(vec![], 233u32);
    let s = plain_node(vec![('t', leaf)]);
    let e = plain_node(vec![('s', s)]);
    let t = plain_node(vec![('e', e)]);
    Trie::from_root(Some(plain_node(vec![('t', t)])))
}

#[test]
fn s0a_01_an_empty_trie_has_no_values() {
    let trie = t();
    assert!(trie.get::<u32>("").is_none());
    assert!(trie.get::<u32>("anything").is_none());
    assert!(trie.root().is_none());
}

#[test]
fn s0a_01_get_finds_the_value_at_the_end_of_the_key() {
    assert_eq!(test_trie().get::<u32>("test"), Some(&233));
}

#[test]
fn s0a_01_a_prefix_that_holds_no_value_is_not_found() {
    let trie = test_trie();
    assert!(trie.get::<u32>("te").is_none(), "te only leads to test");
    assert!(trie.get::<u32>("tests").is_none(), "the key is longer than any stored");
    assert!(trie.get::<u32>("").is_none());
    assert!(trie.get::<u32>("tx").is_none());
}

#[test]
fn s0a_01_the_requested_type_must_match_the_stored_one() {
    let trie = test_trie();
    assert!(trie.get::<String>("test").is_none());
    assert!(trie.get::<u64>("test").is_none());
    assert_eq!(trie.get::<u32>("test"), Some(&233));
}

#[test]
fn s0a_01_the_empty_key_lives_in_the_root() {
    let trie = Trie::from_root(Some(value_node(vec![('a', value_node(vec![], 1u32))], String::from("empty-key"))));
    assert_eq!(trie.get::<String>(""), Some(&String::from("empty-key")));
    assert_eq!(trie.get::<u32>("a"), Some(&1));
}

#[test]
fn s0a_01_a_node_can_have_a_value_and_children_and_both_are_found() {
    let trie = Trie::from_root(Some(plain_node(vec![('a', value_node(vec![('b', value_node(vec![], 2u32))], 1u32))])));
    assert_eq!(trie.get::<u32>("a"), Some(&1));
    assert_eq!(trie.get::<u32>("ab"), Some(&2));
}

#[test]
fn s0a_01_get_shared_gives_an_owner_of_the_value() {
    let trie = Trie::from_root(Some(plain_node(vec![('k', value_node(vec![], String::from("v")))])));
    let shared = trie.get_shared::<String>("k").unwrap();
    drop(trie);
    assert_eq!(*shared, "v", "the value outlives the trie it came from");
    assert!(test_trie().get_shared::<String>("test").is_none());
}

// ---- 0a-02: put -------------------------------------------------------------------------------------------------------------------------

#[test]
fn s0a_02_put_builds_one_node_per_character() {
    let trie = t().put("test", 233u32);
    let mut node = trie.root().unwrap();
    for c in ['t', 'e', 's', 't'] {
        assert_eq!(node.children.len(), 1);
        assert!(!node.is_value_node());
        node = node.children.get(&c).unwrap();
    }
    assert!(node.children.is_empty());
    assert!(node.is_value_node());
}

#[test]
fn s0a_02_put_replaces_a_value_even_with_another_type() {
    let trie = t().put("test", 233u32).put("test", 23333333u32);
    assert_eq!(trie.get::<u32>("test"), Some(&23333333));
    let trie = trie.put("test", String::from("23333333"));
    assert_eq!(trie.get::<String>("test"), Some(&String::from("23333333")));
    assert!(trie.get::<u32>("test").is_none());
}

#[test]
fn s0a_02_keys_that_are_prefixes_of_each_other_share_a_path() {
    let trie = t().put("111", 111u32).put("11", 11u32).put("1111", 1111u32).put("11", 22u32);
    assert_eq!(trie.get::<u32>("11"), Some(&22));
    assert_eq!(trie.get::<u32>("111"), Some(&111));
    assert_eq!(trie.get::<u32>("1111"), Some(&1111));
    assert!(trie.get::<u32>("1").is_none());
}

#[test]
fn s0a_02_putting_never_changes_the_old_trie() {
    let one = t().put("test", 2333u32);
    let two = one.put("te", 23u32);
    let three = two.put("tes", 233u32);
    assert!(one.get::<u32>("te").is_none());
    assert!(two.get::<u32>("tes").is_none());
    assert_eq!(three.get::<u32>("te"), Some(&23));
    assert_eq!(three.get::<u32>("tes"), Some(&233));
    assert_eq!(three.get::<u32>("test"), Some(&2333));
}

#[test]
fn s0a_02_overwriting_keeps_the_other_versions_values() {
    let base = t().put("test", 2333u32).put("te", 23u32).put("tes", 233u32);
    let a = base.put("te", String::from("23"));
    let b = base.put("tes", String::from("233"));
    let c = base.put("test", String::from("2333"));
    assert_eq!(base.get::<u32>("te"), Some(&23));
    assert_eq!(a.get::<String>("te").map(String::as_str), Some("23"));
    assert_eq!(a.get::<u32>("tes"), Some(&233));
    assert_eq!(b.get::<String>("tes").map(String::as_str), Some("233"));
    assert_eq!(b.get::<u32>("test"), Some(&2333));
    assert_eq!(c.get::<String>("test").map(String::as_str), Some("2333"));
}

#[test]
fn s0a_02_only_the_path_is_copied_everything_else_is_shared() {
    let base = t().put("ab", 1u32).put("ac", 2u32).put("xy", 3u32);
    let next = base.put("ab", 10u32);
    let (old_root, new_root) = (base.root().unwrap(), next.root().unwrap());
    assert!(!Arc::ptr_eq(old_root, new_root), "the root is on the path");
    assert!(Arc::ptr_eq(&old_root.children[&'x'], &new_root.children[&'x']), "the x branch is shared");
    assert!(Arc::ptr_eq(&old_root.children[&'a'].children[&'c'], &new_root.children[&'a'].children[&'c']), "the sibling leaf is shared");
    assert!(!Arc::ptr_eq(&old_root.children[&'a'], &new_root.children[&'a']));
}

#[test]
fn s0a_02_values_are_not_copied_and_need_not_be_clonable() {
    struct NoClone(u32);
    let trie = t().put("tes", Box::new(NoClone(233))).put("te", Box::new(NoClone(23))).put("test", Box::new(NoClone(2333)));
    assert_eq!(trie.get::<Box<NoClone>>("te").unwrap().0, 23);
    assert_eq!(trie.get::<Box<NoClone>>("test").unwrap().0, 2333);
    let before = trie.get::<Box<NoClone>>("test").unwrap() as *const _;
    let trie = trie.put("tes", Box::new(NoClone(0)));
    let after = trie.get::<Box<NoClone>>("test").unwrap() as *const _;
    assert_eq!(before, after, "the value of an untouched key keeps its address");
}

// ---- 0a-03: remove ----------------------------------------------------------------------------------------------------------------------

#[test]
fn s0a_03_remove_deletes_only_the_given_key() {
    let trie = t().put("test", 2333u32).put("te", 23u32).put("tes", 233u32).remove("tes");
    assert!(trie.get::<u32>("tes").is_none());
    assert_eq!(trie.get::<u32>("te"), Some(&23));
    assert_eq!(trie.get::<u32>("test"), Some(&2333));
}

#[test]
fn s0a_03_removing_everything_leaves_an_empty_trie_with_no_root() {
    let mut trie = t().put("test", 2333u32).put("te", 23u32).put("tes", 233u32).put("", 123u32);
    for k in ["", "te", "tes", "test"] {
        trie = trie.remove(k);
    }
    assert!(trie.root().is_none());
    for k in ["", "te", "tes", "test"] {
        assert!(trie.get::<u32>(k).is_none());
    }
}

#[test]
fn s0a_03_nodes_with_no_value_and_no_children_are_pruned() {
    let trie = t().put("test", 2333u32).put("te", 23u32).put("tes", 233u32).remove("tes").remove("test");
    let te = &trie.root().unwrap().children[&'t'].children[&'e'];
    assert!(te.children.is_empty(), "s and t were pruned");
    assert!(te.is_value_node());
}

#[test]
fn s0a_03_a_node_that_still_leads_somewhere_stays() {
    let trie = t().put("test", 1u32).put("te", 2u32).remove("te");
    assert!(trie.get::<u32>("te").is_none());
    assert_eq!(trie.get::<u32>("test"), Some(&1));
    assert!(!trie.root().unwrap().children[&'t'].children[&'e'].is_value_node());
}

#[test]
fn s0a_03_removing_a_missing_key_changes_nothing() {
    let trie = t().put("test", 1u32);
    for k in ["tes", "tests", "x", ""] {
        let same = trie.remove(k);
        assert_eq!(same.get::<u32>("test"), Some(&1), "{k}");
    }
    assert!(t().remove("x").root().is_none());
}

#[test]
fn s0a_03_removing_never_changes_the_old_trie() {
    let trie3 = t().put("test", 2333u32).put("te", 23u32).put("tes", 233u32);
    let trie4 = trie3.remove("te");
    let trie5 = trie3.remove("tes");
    let trie6 = trie3.remove("test");
    assert_eq!(trie3.get::<u32>("te"), Some(&23));
    assert!(trie4.get::<u32>("te").is_none());
    assert_eq!(trie4.get::<u32>("tes"), Some(&233));
    assert!(trie5.get::<u32>("tes").is_none());
    assert_eq!(trie5.get::<u32>("test"), Some(&2333));
    assert!(trie6.get::<u32>("test").is_none());
    assert_eq!(trie6.get::<u32>("te"), Some(&23));
}

// ---- 0a-04: the store ------------------------------------------------------------------------------------------------------------------

#[test]
fn s0a_04_put_get_remove() {
    let store = TrieStore::new();
    assert!(store.get::<u32>("233").is_none());
    store.put("233", 2333u32);
    assert_eq!(*store.get::<u32>("233").unwrap(), 2333);
    store.remove("233");
    assert!(store.get::<u32>("233").is_none());
}

#[test]
fn s0a_04_a_guard_stays_valid_after_the_key_is_removed() {
    let store = TrieStore::new();
    store.put("233", String::from("2333"));
    let guard = store.get::<String>("233").unwrap();
    store.remove("233");
    assert!(store.get::<String>("233").is_none());
    assert_eq!(*guard, "2333");
}

#[test]
fn s0a_04_a_guard_sees_the_version_it_was_taken_from() {
    let store = TrieStore::new();
    store.put("k", 1u32);
    let old = store.get::<u32>("k").unwrap();
    store.put("k", 2u32);
    assert_eq!(*old, 1);
    assert_eq!(*store.get::<u32>("k").unwrap(), 2);
}

#[test]
fn s0a_04_values_need_not_be_clonable() {
    struct NoClone(u32);
    let store = TrieStore::new();
    store.put("tes", Box::new(NoClone(233)));
    store.put("te", Box::new(NoClone(23)));
    assert_eq!(store.get::<Box<NoClone>>("te").unwrap().0, 23);
    store.remove("te");
    assert!(store.get::<Box<NoClone>>("te").is_none());
}

#[test]
fn s0a_04_four_writers_and_four_readers() {
    let store = Arc::new(TrieStore::new());
    let per_thread = 2_000u32;
    let key = |n: u32| format!("{n:05}");
    let writers: Vec<_> = (0..4u32)
        .map(|tid| {
            let store = store.clone();
            std::thread::spawn(move || {
                for i in 0..per_thread {
                    store.put(&key(i * 4 + tid), format!("value-{:08}", i * 4 + tid));
                }
                for i in 0..per_thread {
                    store.remove(&key(i * 4 + tid));
                }
                for i in 0..per_thread {
                    store.put(&key(i * 4 + tid), format!("new-value-{:08}", i * 4 + tid));
                }
            })
        })
        .collect();
    let stop = Arc::new(AtomicBool::new(false));
    let readers: Vec<_> = (0..4u32)
        .map(|tid| {
            let (store, stop) = (store.clone(), stop.clone());
            std::thread::spawn(move || {
                let mut i = 0;
                while !stop.load(Ordering::Relaxed) {
                    store.get::<String>(&key(i * 4 + tid));
                    i = (i + 1) % per_thread;
                }
            })
        })
        .collect();
    for w in writers {
        w.join().unwrap();
    }
    stop.store(true, Ordering::Relaxed);
    for r in readers {
        r.join().unwrap();
    }
    for i in 0..per_thread * 4 {
        let guard = store.get::<String>(&key(i)).unwrap_or_else(|| panic!("key {i} was lost: two writers started from the same version"));
        assert_eq!(*guard, format!("new-value-{i:08}"));
    }
}

#[test]
fn s0a_04_readers_are_not_blocked_by_a_writer_building_a_big_trie() {
    let store = Arc::new(TrieStore::new());
    for i in 0..1000u32 {
        store.put(&format!("{i:04}"), i);
    }
    let writer = {
        let store = store.clone();
        std::thread::spawn(move || {
            for i in 1000..6000u32 {
                store.put(&format!("{i:04}"), i);
            }
        })
    };
    // while the writer runs, readers keep finding what is already there
    while !writer.is_finished() {
        for i in (0..1000u32).step_by(97) {
            assert_eq!(*store.get::<u32>(&format!("{i:04}")).unwrap(), i);
        }
    }
    writer.join().unwrap();
}

// ---- 0a-05: BusTub's trie tests ---------------------------------------------------------------------------------------------------------

#[test]
fn s0a_05_mixed_test() {
    let mut trie = Trie::new();
    for i in 0..23333u32 {
        trie = trie.put(&format!("{i:05}"), format!("value-{i:08}"));
    }
    let full = trie.clone();
    for i in (0..23333u32).step_by(2) {
        trie = trie.put(&format!("{i:05}"), format!("new-value-{i:08}"));
    }
    let overridden = trie.clone();
    for i in (0..23333u32).step_by(3) {
        trie = trie.remove(&format!("{i:05}"));
    }
    let fin = trie;
    for i in 0..23333u32 {
        let key = format!("{i:05}");
        assert_eq!(full.get::<String>(&key), Some(&format!("value-{i:08}")));
        let want = if i % 2 == 0 { format!("new-value-{i:08}") } else { format!("value-{i:08}") };
        assert_eq!(overridden.get::<String>(&key), Some(&want));
        if i % 3 == 0 {
            assert!(fin.get::<String>(&key).is_none());
        } else {
            assert_eq!(fin.get::<String>(&key), Some(&want));
        }
    }
}

#[test]
fn s0a_05_copy_on_write_tests_with_the_empty_key() {
    let trie3 = Trie::new().put("test", 2333u32).put("te", 23u32).put("", 233u32);
    let trie4 = trie3.put("te", String::from("23"));
    let trie5 = trie3.put("", String::from("233"));
    let trie6 = trie3.put("test", String::from("2333"));
    assert_eq!(trie3.get::<u32>("te"), Some(&23));
    assert_eq!(trie3.get::<u32>(""), Some(&233));
    assert_eq!(trie3.get::<u32>("test"), Some(&2333));
    assert_eq!(trie4.get::<String>("te").map(String::as_str), Some("23"));
    assert_eq!(trie4.get::<u32>(""), Some(&233));
    assert_eq!(trie5.get::<String>("").map(String::as_str), Some("233"));
    assert_eq!(trie5.get::<u32>("test"), Some(&2333));
    assert_eq!(trie6.get::<String>("test").map(String::as_str), Some("2333"));
    assert_eq!(trie6.get::<u32>(""), Some(&233));
}

#[test]
fn s0a_05_trie_store_mixed_test() {
    let store = TrieStore::new();
    for i in 0..23333u32 {
        store.put(&format!("{i:05}"), format!("value-{i:08}"));
    }
    for i in (0..23333u32).step_by(2) {
        store.put(&format!("{i:05}"), format!("new-value-{i:08}"));
    }
    for i in (0..23333u32).step_by(3) {
        store.remove(&format!("{i:05}"));
    }
    for i in 0..23333u32 {
        let key = format!("{i:05}");
        let got = store.get::<String>(&key);
        if i % 3 == 0 {
            assert!(got.is_none());
        } else if i % 2 == 0 {
            assert_eq!(*got.unwrap(), format!("new-value-{i:08}"));
        } else {
            assert_eq!(*got.unwrap(), format!("value-{i:08}"));
        }
    }
}

#[test]
fn s0a_05_pointer_stability_and_noncopyable_values() {
    let trie = Trie::new().put("test", 2333u32);
    let before = trie.get::<u32>("test").unwrap() as *const u32;
    let trie = trie.put("tes", 233u32).put("te", 23u32);
    let after = trie.get::<u32>("test").unwrap() as *const u32;
    assert_eq!(before, after);
    let boxed = Trie::new().put("tes", Box::new(233u32)).put("te", Box::new(23u32)).put("test", Box::new(2333u32));
    assert_eq!(**boxed.get::<Box<u32>>("te").unwrap(), 23);
    let boxed = boxed.remove("te").remove("tes").remove("test");
    assert!(boxed.get::<Box<u32>>("te").is_none());
}
