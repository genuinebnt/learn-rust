use solution::*;

#[test]
fn empty() {
    check!(r#"xs = []"#, { let mut s = Stats { values: vec![], total: 1.0, max: 0.0 }; s.record_all(&[]); (s.values.len(), s.total) }, (0, 1.0));
}
