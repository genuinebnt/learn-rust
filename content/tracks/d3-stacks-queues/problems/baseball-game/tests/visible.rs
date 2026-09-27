use solution::*;

#[test]
fn example() {
    check!(r#"["5","2","C","D","+"]"#, cal_points(&["5", "2", "C", "D", "+"]), Some(30));
}

#[test]
fn negatives() {
    check!(r#"["5","-2","4","C","D","9","+","+"]"#, cal_points(&["5", "-2", "4", "C", "D", "9", "+", "+"]), Some(27));
}

#[test]
fn cancel_all() {
    check!(r#"["1","C"]"#, cal_points(&["1", "C"]), Some(0));
}

#[test]
fn plus_too_early() {
    check!(r#"["1","+"]"#, cal_points(&["1", "+"]), None);
}

#[test]
fn double_needs_a_score() {
    check!(r#"["D"]"#, cal_points(&["D"]), None);
}
