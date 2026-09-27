use solution::*;

#[test]
fn right_survives() {
    check!(r#"[5,10,-5]"#, asteroid_collision(&[5, 10, -5]), vec![5, 10]);
}

#[test]
fn both_explode() {
    check!(r#"[8,-8]"#, asteroid_collision(&[8, -8]), vec![]);
}

#[test]
fn chain() {
    check!(r#"[10,2,-5]"#, asteroid_collision(&[10, 2, -5]), vec![10]);
}

#[test]
fn left_mover_survives() {
    check!(r#"[3,5,-6,2,-1,4]"#, asteroid_collision(&[3, 5, -6, 2, -1, 4]), vec![-6, 2, 4]);
}

#[test]
fn moving_apart() {
    check!(r#"[-2,-1,1,2]"#, asteroid_collision(&[-2, -1, 1, 2]), vec![-2, -1, 1, 2]);
}
