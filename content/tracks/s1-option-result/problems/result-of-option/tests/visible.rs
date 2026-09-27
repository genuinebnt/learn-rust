use solution::*;

#[test]
fn require_present() {
    check!(r#"store = {a: "5"}, require("a")"#, require(&Store::new(&[("a", "5")]), "a"), Ok(5));
}

#[test]
fn require_missing() {
    check!(r#"store = {a: "5"}, require("b")"#, require(&Store::new(&[("a", "5")]), "b"), Err(StoreError::Missing("b".to_string())));
}

#[test]
fn require_corrupt() {
    check!(r#"store = {a: "x"}, require("a")"#, require(&Store::new(&[("a", "x")]), "a"), Err(StoreError::Corrupt("a".to_string())));
}

#[test]
fn sum_counts_missing_as_zero() {
    check!(r#"store = {a: "5", b: "-2"}, sum_or_zero(["a", "b", "c"])"#, sum_or_zero(&Store::new(&[("a", "5"), ("b", "-2")]), &["a", "b", "c"]), Ok(3));
}

#[test]
fn sum_stops_at_corrupt() {
    check!(r#"store = {a: "1", b: "x"}, sum_or_zero(["a", "b"])"#, sum_or_zero(&Store::new(&[("a", "1"), ("b", "x")]), &["a", "b"]), Err(StoreError::Corrupt("b".to_string())));
}
