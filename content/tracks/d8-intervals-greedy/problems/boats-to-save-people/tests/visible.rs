use solution::*;

#[test]
fn leetcode_one_boat() {
    check!(r#"people = [1, 2], limit = 3"#, num_rescue_boats(&[1, 2], 3), 1);
}

#[test]
fn leetcode_three() {
    check!(r#"people = [3, 2, 2, 1], limit = 3"#, num_rescue_boats(&[3, 2, 2, 1], 3), 3);
}

#[test]
fn leetcode_four() {
    check!(r#"people = [3, 5, 3, 4], limit = 5"#, num_rescue_boats(&[3, 5, 3, 4], 5), 4);
}

#[test]
fn nobody() {
    check!(r#"people = [], limit = 5"#, num_rescue_boats(&[], 5), 0);
}

#[test]
fn one_person() {
    check!(r#"people = [5], limit = 5"#, num_rescue_boats(&[5], 5), 1);
}

#[test]
fn at_most_two_per_boat() {
    check!(r#"people = [1, 1, 1], limit = 3"#, num_rescue_boats(&[1, 1, 1], 3), 2);
}
