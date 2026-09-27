use solution::*;

#[test]
fn leetcode_apple() {
    let mut t = Trie::new();
    t.insert("apple");
    t.insert("apple");
    let (a, b) = (t.count_words_equal_to("apple"), t.count_words_starting_with("app"));
    t.erase("apple");
    let (c, d) = (t.count_words_equal_to("apple"), t.count_words_starting_with("app"));
    t.erase("apple");
    check!(r#"insert apple, apple; equal apple; starting app; erase apple; equal apple; starting app; erase apple; starting app"#, (a, b, c, d, t.count_words_starting_with("app")), (2, 2, 1, 1, 0));
}

#[test]
fn empty_trie() {
    let t = Trie::new();
    check!(r#"new trie; equal "a", starting "a", starting """#, (t.count_words_equal_to("a"), t.count_words_starting_with("a"), t.count_words_starting_with("")), (0, 0, 0));
}

#[test]
fn erase_missing_changes_nothing() {
    let mut t = Trie::new();
    t.insert("apple");
    let erased = t.erase("app");
    check!(r#"insert apple; erase "app"; starting "app", equal "apple""#, (erased, t.count_words_starting_with("app"), t.count_words_equal_to("apple")), (false, 1, 1));
}

#[test]
fn every_copy_counts() {
    let mut t = Trie::new();
    for w in ["a", "ab", "ab", "abc"] {
        t.insert(w);
    }
    check!(r#"insert a, ab, ab, abc; starting "a", starting "ab", equal "ab""#, (t.count_words_starting_with("a"), t.count_words_starting_with("ab"), t.count_words_equal_to("ab")), (4, 3, 2));
}

#[test]
fn erase_returns_true_then_false() {
    let mut t = Trie::new();
    t.insert("x");
    let first = t.erase("x");
    check!(r#"insert x; erase x; erase x"#, (first, t.erase("x")), (true, false));
}

#[test]
fn erase_keeps_longer_word() {
    let mut t = Trie::new();
    t.insert("ab");
    t.insert("abc");
    t.erase("ab");
    check!(r#"insert ab, abc; erase ab; equal abc, starting ab"#, (t.count_words_equal_to("abc"), t.count_words_starting_with("ab")), (1, 1));
}
