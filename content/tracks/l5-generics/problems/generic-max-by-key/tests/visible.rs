use solution::*;

#[test]
fn longest_word() {
    check!(r#"["apple", "fig", "banana"], key = len"#, max_by_key(&["apple", "fig", "banana"], |w| w.len()), Some(&"banana"));
}

#[test]
fn empty() {
    check!(r#"[], key = identity"#, max_by_key(&[] as &[i32], |x| *x), None);
}

#[test]
fn tie_returns_the_first() {
    check!(r#"["ab", "cd", "e"], key = len"#, max_by_key(&["ab", "cd", "e"], |w| w.len()), Some(&"ab"));
}

#[test]
fn key_called_once_per_item() {
    let v = [4, 9, 2, 9];
    let mut calls = 0;
    let best = max_by_key(&v, |x| {
        calls += 1;
        *x
    }).copied();
    check!(r#"[4, 9, 2, 9], count the calls"#, (best, calls), (Some(9), 4));
}

#[test]
fn owned_string_key() {
    let people = [("ada", 36), ("Zed", 31), ("bob", 25)];
    check!(r#"people by name, key = name.to_lowercase()"#, max_by_key(&people, |p| p.0.to_lowercase()).map(|p| p.1), Some(31));
}
