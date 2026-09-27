use solution::*;

#[test]
fn insert_and_find() {
    let mut t = Trie::new();
    t.insert("car");
    check!(r#"insert "car"; contains "car""#, t.contains("car"), true);
}

#[test]
fn empty_trie() {
    let t = Trie::new();
    check!(r#"new trie; contains "a""#, t.contains("a"), false);
}

#[test]
fn prefix_is_not_a_word() {
    let mut t = Trie::new();
    t.insert("car");
    check!(r#"insert "car"; contains "ca""#, t.contains("ca"), false);
}

#[test]
fn shared_prefix_keeps_both() {
    let mut t = Trie::new();
    t.insert("car");
    t.insert("cart");
    check!(r#"insert "car", "cart"; contains both"#, (t.contains("car"), t.contains("cart")), (true, true));
}

#[test]
fn longer_first() {
    let mut t = Trie::new();
    t.insert("cart");
    t.insert("car");
    check!(r#"insert "cart", "car"; contains both"#, (t.contains("car"), t.contains("cart")), (true, true));
}
