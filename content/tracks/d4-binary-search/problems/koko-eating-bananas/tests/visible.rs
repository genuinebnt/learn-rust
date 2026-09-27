use solution::*;

#[test]
fn four() {
    check!(r#"[3,6,7,11], 8 hours"#, min_eating_speed(&[3, 6, 7, 11], 8), Some(4));
}

#[test]
fn tight() {
    check!(r#"[30,11,23,4,20], 5 hours"#, min_eating_speed(&[30, 11, 23, 4, 20], 5), Some(30));
}
