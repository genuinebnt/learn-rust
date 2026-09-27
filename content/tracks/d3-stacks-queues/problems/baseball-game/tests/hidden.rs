use solution::*;

#[test]
fn plus_too_early() {
    check!(r#"["1","+"]"#, cal_points(&["1", "+"]), None);
}

#[test]
fn not_a_number() {
    check!(r#"["x"]"#, cal_points(&["x"]), None);
}

#[test]
fn cancel_all() {
    check!(r#"["1","C"]"#, cal_points(&["1", "C"]), Some(0));
}

#[test]
fn cancel_nothing() {
    check!(r#"["C"]"#, cal_points(&["C"]), None);
}
