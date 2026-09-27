use solution::*;

#[test]
fn cycle() {
    check!(r#"0→1→2→3→1"#, cycle_start(&[Some(1), Some(2), Some(3), Some(1)], Some(0)), Some(1));
}

#[test]
fn no_cycle() {
    check!(r#"0→1→end"#, (cycle_start(&[Some(1), None], Some(0)), has_cycle(&[Some(1), None], Some(0))), (None, false));
}

#[test]
fn two_node_cycle() {
    check!(r#"0→1→0"#, (cycle_start(&[Some(1), Some(0)], Some(0)), has_cycle(&[Some(1), Some(0)], Some(0))), (Some(0), true));
}

#[test]
fn single_no_cycle() {
    check!(r#"0→end"#, cycle_start(&[None], Some(0)), None);
}

#[test]
fn empty() {
    check!(r#"no head"#, cycle_start(&[], None), None);
}
