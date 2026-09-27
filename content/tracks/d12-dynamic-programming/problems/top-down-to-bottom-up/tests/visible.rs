use solution::*;

#[test]
fn three_at_a_time() {
    check!(r#"heights = [10, 30, 40, 50, 20], k = 3"#, min_cost(&[10, 30, 40, 50, 20], 3), 30);
}

#[test]
fn two_at_a_time() {
    check!(r#"heights = [10, 30, 40, 20], k = 2"#, min_cost(&[10, 30, 40, 20], 2), 30);
}

#[test]
fn one_at_a_time() {
    check!(r#"heights = [10, 20, 10], k = 1"#, min_cost(&[10, 20, 10], 1), 20);
}

#[test]
fn already_there() {
    check!(r#"heights = [5], k = 1"#, min_cost(&[5], 1), 0);
}

#[test]
fn no_stones() {
    check!(r#"heights = [], k = 3"#, min_cost(&[], 3), 0);
}
