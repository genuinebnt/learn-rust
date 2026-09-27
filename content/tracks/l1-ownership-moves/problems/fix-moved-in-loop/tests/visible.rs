use solution::*;

#[test]
fn example() {
    check!(r#"[("a", 1), ("a", 2), ("b", 3), ("a", 4)]"#, group_runs(vec![("a".to_string(), 1), ("a".to_string(), 2), ("b".to_string(), 3), ("a".to_string(), 4)]), (vec![("a".to_string(), vec![1, 2]), ("b".to_string(), vec![3]), ("a".to_string(), vec![4])], 4));
}

#[test]
fn empty() {
    check!(r#"[]"#, group_runs(vec![]), (vec![], 0));
}

#[test]
fn one_record() {
    check!(r#"[("x", 9)]"#, group_runs(vec![("x".to_string(), 9)]), (vec![("x".to_string(), vec![9])], 1));
}

#[test]
fn all_same_key() {
    check!(r#"[("k", 1), ("k", 2), ("k", 3)]"#, group_runs(vec![("k".to_string(), 1), ("k".to_string(), 2), ("k".to_string(), 3)]), (vec![("k".to_string(), vec![1, 2, 3])], 3));
}

#[test]
fn all_different() {
    check!(r#"[("a", 1), ("b", 2), ("c", 3)]"#, group_runs(vec![("a".to_string(), 1), ("b".to_string(), 2), ("c".to_string(), 3)]), (vec![("a".to_string(), vec![1]), ("b".to_string(), vec![2]), ("c".to_string(), vec![3])], 3));
}
