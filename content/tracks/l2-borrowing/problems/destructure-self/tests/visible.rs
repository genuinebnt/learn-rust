use solution::*;

#[test]
fn records() {
    check!(r#"xs = [1.5, 4.0, 2.5]"#, { let mut s = Stats { values: vec![], total: 0.0, max: f64::MIN }; s.record_all(&[1.5, 4.0, 2.5]); (s.values.len(), s.total, s.max) }, (3, 8.0, 4.0));
}

#[test]
fn keeps_max() {
    check!(r#"max 10, xs = [3]"#, { let mut s = Stats { values: vec![], total: 0.0, max: 10.0 }; s.record_all(&[3.0]); s.max }, 10.0);
}

#[test]
fn negatives() {
    check!(r#"max f64::MIN, xs = [-2.0, -1.0]"#, { let mut s = Stats { values: vec![], total: 0.0, max: f64::MIN }; s.record_all(&[-2.0, -1.0]); (s.total, s.max) }, (-3.0, -1.0));
}

#[test]
fn total_accumulates() {
    check!(r#"total 10.0, xs = [1.0, 2.0]"#, { let mut s = Stats { values: vec![], total: 10.0, max: 0.0 }; s.record_all(&[1.0, 2.0]); s.total }, 13.0);
}

#[test]
fn empty() {
    check!(r#"xs = []"#, { let mut s = Stats { values: vec![], total: 1.0, max: 0.0 }; s.record_all(&[]); (s.values.len(), s.total) }, (0, 1.0));
}
