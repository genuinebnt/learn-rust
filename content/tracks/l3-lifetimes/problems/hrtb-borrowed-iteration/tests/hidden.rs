use solution::*;

#[test]
fn array() {
    check!(r#"[4, 4, 4]"#, Stats::new([4u32, 4, 4]).spread(), Some(0));
}

#[test]
fn btreeset() {
    check!(r#"BTreeSet {1, 10}"#, Stats::new(std::collections::BTreeSet::from([1u32, 10])).mean(), Some(5.5));
}

#[test]
fn empty() {
    check!(r#"empty Vec"#, Stats::new(Vec::<u32>::new()).mean(), None);
}

#[test]
fn count() {
    check!(r#"[1, 5, 9], above 4"#, Stats::new(vec![1u32, 5, 9]).count_above(4), 2);
}

#[test]
fn reuse() {
    let s = Stats::new(vec![1u32, 2, 3]);
    check!(r#"call three methods on the same Stats"#, (s.mean(), s.spread(), s.count_above(0)), (Some(2.0), Some(2), 3));
}
