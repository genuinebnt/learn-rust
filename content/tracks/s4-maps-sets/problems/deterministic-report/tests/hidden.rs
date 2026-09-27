use solution::*;

#[test]
fn many_ties() {
    check!(r#"{d: 1, c: 1, b: 1, a: 1}"#, report(&std::collections::HashMap::from([("d".to_string(), 1), ("c".to_string(), 1), ("b".to_string(), 1), ("a".to_string(), 1)])), vec!["a: 1", "b: 1", "c: 1", "d: 1"]);
}
