use solution::*;

#[test]
fn chain() {
    check!(r#"[10,2,-5]"#, asteroid_collision(&[10, 2, -5]), vec![10]);
}

#[test]
fn moving_apart() {
    check!(r#"[-2,-1,1,2]"#, asteroid_collision(&[-2, -1, 1, 2]), vec![-2, -1, 1, 2]);
}

#[test]
fn left_wins() {
    check!(r#"[1,-2,-2,-2]"#, asteroid_collision(&[1, -2, -2, -2]), vec![-2, -2, -2]);
}
