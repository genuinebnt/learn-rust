use solution::*;

#[test]
fn leetcode_apple() {
    let mut t = Trie::new();
    t.insert("apple");
    let (a, b, c) = (t.search("apple"), t.search("app"), t.starts_with("app"));
    t.insert("app");
    check!(r#"insert "apple"; search "apple", search "app", starts_with "app"; insert "app"; search "app""#, (a, b, c, t.search("app")), (true, false, true, true));
}

#[test]
fn empty_trie() {
    let t = Trie::new();
    check!(r#"new trie; search "a", starts_with "a""#, (t.search("a"), t.starts_with("a")), (false, false));
}

#[test]
fn prefix_is_not_a_word() {
    let mut t = Trie::new();
    t.insert("apple");
    check!(r#"insert "apple"; search "app""#, t.search("app"), false);
}

#[test]
fn word_is_its_own_prefix() {
    let mut t = Trie::new();
    t.insert("apple");
    check!(r#"insert "apple"; starts_with "apple""#, t.starts_with("apple"), true);
}

#[test]
fn longer_than_any_word() {
    let mut t = Trie::new();
    t.insert("app");
    check!(r#"insert "app"; search "apple", starts_with "apple""#, (t.search("apple"), t.starts_with("apple")), (false, false));
}

#[test]
fn empty_prefix() {
    let t = Trie::new();
    check!(r#"new trie; starts_with "", search """#, (t.starts_with(""), t.search("")), (true, false));
}
