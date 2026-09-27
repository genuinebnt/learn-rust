use solution::*;

#[test]
fn leetcode_seven() {
    check!(r#"n = 7, cuts = [1, 3, 4, 5]"#, min_cost(7, &[1, 3, 4, 5]), 16);
}

#[test]
fn leetcode_nine() {
    check!(r#"n = 9, cuts = [5, 6, 1, 4, 2]"#, min_cost(9, &[5, 6, 1, 4, 2]), 22);
}

#[test]
fn no_cuts() {
    check!(r#"n = 5, cuts = []"#, min_cost(5, &[]), 0);
}

#[test]
fn one_cut() {
    check!(r#"n = 2, cuts = [1]"#, min_cost(2, &[1]), 2);
}

#[test]
fn order_matters() {
    check!(r#"n = 10, cuts = [2, 5] (cutting 5 first is cheaper)"#, min_cost(10, &[2, 5]), 15);
}
