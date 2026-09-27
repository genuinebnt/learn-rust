use solution::*;

#[test]
fn ordered() {
    check!(r#"{ann: 5, bob: 9, cy: 5}"#, report(&std::collections::HashMap::from([("ann".to_string(), 5), ("bob".to_string(), 9), ("cy".to_string(), 5)])), vec!["bob: 9", "ann: 5", "cy: 5"]);
}

#[test]
fn empty() {
    check!(r#"{}"#, report(&std::collections::HashMap::new()), Vec::<String>::new());
}

#[test]
fn many_ties() {
    check!(r#"{d: 1, c: 1, b: 1, a: 1}"#, report(&std::collections::HashMap::from([("d".to_string(), 1), ("c".to_string(), 1), ("b".to_string(), 1), ("a".to_string(), 1)])), vec!["a: 1", "b: 1", "c: 1", "d: 1"]);
}

#[test]
fn single() {
    check!(r#"{x: 0}"#, report(&std::collections::HashMap::from([("x".to_string(), 0)])), vec!["x: 0"]);
}

#[test]
fn highest_first() {
    check!(r#"{a: 1, b: 2}"#, report(&std::collections::HashMap::from([("a".to_string(), 1), ("b".to_string(), 2)])), vec!["b: 2", "a: 1"]);
}
