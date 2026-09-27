use solution::*;

#[test]
fn right_survives() {
    check!(r#"[5,10,-5]"#, asteroid_collision(&[5, 10, -5]), vec![5, 10]);
}

#[test]
fn both_explode() {
    check!(r#"[8,-8]"#, asteroid_collision(&[8, -8]), vec![]);
}
