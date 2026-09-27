use solution::*;

#[test]
fn leetcode_three_runs() {
    check!(r#"hand = [1, 2, 3, 6, 2, 3, 4, 7, 8], group_size = 3"#, is_n_straight_hand(&[1, 2, 3, 6, 2, 3, 4, 7, 8], 3), true);
}

#[test]
fn leetcode_wrong_size() {
    check!(r#"hand = [1, 2, 3, 4, 5], group_size = 4"#, is_n_straight_hand(&[1, 2, 3, 4, 5], 4), false);
}

#[test]
fn empty_hand() {
    check!(r#"hand = [], group_size = 3"#, is_n_straight_hand(&[], 3), true);
}

#[test]
fn groups_of_one() {
    check!(r#"hand = [5, 5, 1], group_size = 1"#, is_n_straight_hand(&[5, 5, 1], 1), true);
}

#[test]
fn duplicates_make_two_runs() {
    check!(r#"hand = [1, 1, 2, 2, 3, 3], group_size = 3"#, is_n_straight_hand(&[1, 1, 2, 2, 3, 3], 3), true);
}

#[test]
fn gap_breaks_the_run() {
    check!(r#"hand = [1, 2, 4], group_size = 3"#, is_n_straight_hand(&[1, 2, 4], 3), false);
}
