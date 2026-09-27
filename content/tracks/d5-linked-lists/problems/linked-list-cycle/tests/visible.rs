use solution::*;

#[test]
fn cycle() {
    check!(r#"0→1→2→3→1"#, cycle_start(&[Some(1), Some(2), Some(3), Some(1)], Some(0)), Some(1));
}

#[test]
fn no_cycle() {
    check!(r#"0→1→end"#, (cycle_start(&[Some(1), None], Some(0)), has_cycle(&[Some(1), None], Some(0))), (None, false));
}
