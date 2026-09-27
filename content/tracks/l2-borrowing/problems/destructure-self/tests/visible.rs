use solution::*;

#[test]
fn records() {
    check!(r#"xs = [1.5, 4.0, 2.5]"#, { let mut s = Stats { values: vec![], total: 0.0, max: f64::MIN }; s.record_all(&[1.5, 4.0, 2.5]); (s.values.len(), s.total, s.max) }, (3, 8.0, 4.0));
}

#[test]
fn keeps_max() {
    check!(r#"max 10, xs = [3]"#, { let mut s = Stats { values: vec![], total: 0.0, max: 10.0 }; s.record_all(&[3.0]); s.max }, 10.0);
}
