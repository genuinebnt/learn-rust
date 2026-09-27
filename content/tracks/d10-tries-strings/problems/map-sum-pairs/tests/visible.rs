use solution::*;

#[test]
fn leetcode_apple() {
    let mut m = MapSum::new();
    m.insert("apple", 3);
    let first = m.sum("ap");
    m.insert("app", 2);
    check!(r#"insert("apple", 3); sum("ap"); insert("app", 2); sum("ap")"#, (first, m.sum("ap")), (3, 5));
}

#[test]
fn overwrite_replaces() {
    let mut m = MapSum::new();
    m.insert("apple", 3);
    m.insert("apple", 2);
    check!(r#"insert("apple", 3); insert("apple", 2); sum("ap")"#, m.sum("ap"), 2);
}

#[test]
fn empty_map() {
    let m = MapSum::new();
    check!(r#"new map; sum("a")"#, m.sum("a"), 0);
}

#[test]
fn prefix_is_the_whole_key() {
    let mut m = MapSum::new();
    m.insert("apple", 3);
    check!(r#"insert("apple", 3); sum("apple")"#, m.sum("apple"), 3);
}

#[test]
fn no_key_matches() {
    let mut m = MapSum::new();
    m.insert("apple", 3);
    check!(r#"insert("apple", 3); sum("b"), sum("apples")"#, (m.sum("b"), m.sum("apples")), (0, 0));
}

#[test]
fn empty_prefix_sums_everything() {
    let mut m = MapSum::new();
    m.insert("a", 1);
    m.insert("b", 2);
    m.insert("c", -4);
    check!(r#"insert("a", 1), ("b", 2), ("c", -4); sum("")"#, m.sum(""), -1);
}
