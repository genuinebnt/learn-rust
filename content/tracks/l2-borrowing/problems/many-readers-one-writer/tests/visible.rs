use solution::*;

#[test]
fn counts() {
    check!(r#"3 slots, hits on 1, 1, 2"#, { let mut c = Counter::new(3); c.hit(1); c.hit(1); c.hit(2); let (a, b) = (&c, &c); (a.total(), b.busiest()) }, (3, Some(1)));
}

#[test]
fn no_hits() {
    check!(r#"2 slots, no hits"#, Counter::new(2).busiest(), Some(0));
}
