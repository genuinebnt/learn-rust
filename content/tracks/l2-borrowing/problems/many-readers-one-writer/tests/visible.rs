use solution::*;

#[test]
fn counts() {
    check!(r#"3 slots, hits on 1, 1, 2"#, { let mut c = Counter::new(3); c.hit(1); c.hit(1); c.hit(2); let (a, b) = (&c, &c); (a.total(), b.busiest()) }, (3, Some(1)));
}

#[test]
fn no_hits() {
    check!(r#"2 slots, no hits"#, Counter::new(2).busiest(), Some(0));
}

#[test]
fn tie_lowest() {
    check!(r#"3 slots, hits on 2, 0"#, { let mut c = Counter::new(3); c.hit(2); c.hit(0); c.busiest() }, Some(0));
}

#[test]
fn last_slot_wins() {
    check!(r#"4 slots, hits on 3, 3, 1"#, { let mut c = Counter::new(4); c.hit(3); c.hit(3); c.hit(1); (c.total(), c.busiest()) }, (3, Some(3)));
}

#[test]
fn no_slots() {
    check!(r#"0 slots"#, (Counter::new(0).total(), Counter::new(0).busiest()), (0, None));
}
