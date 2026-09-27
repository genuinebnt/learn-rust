use solution::*;

#[test]
fn leetcode_two() {
    check!(r#"n = 2"#, climb_stairs(2), 2);
}

#[test]
fn leetcode_three() {
    check!(r#"n = 3"#, climb_stairs(3), 3);
}

#[test]
fn one_step() {
    check!(r#"n = 1"#, climb_stairs(1), 1);
}

#[test]
fn four() {
    check!(r#"n = 4"#, climb_stairs(4), 5);
}

#[test]
fn order_matters() {
    check!(r#"n = 5 (1+2 and 2+1 count separately)"#, climb_stairs(5), 8);
}
