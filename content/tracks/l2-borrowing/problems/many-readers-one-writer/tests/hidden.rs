use solution::*;

#[test]
fn no_slots() {
    check!(r#"0 slots"#, (Counter::new(0).total(), Counter::new(0).busiest()), (0, None));
}
