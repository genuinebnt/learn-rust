use solution::*;

#[test]
fn example() {
    check!(r#"["5","2","C","D","+"]"#, cal_points(&["5", "2", "C", "D", "+"]), Some(30));
}

#[test]
fn negatives() {
    check!(r#"["5","-2","4","C","D","9","+","+"]"#, cal_points(&["5", "-2", "4", "C", "D", "9", "+", "+"]), Some(27));
}
