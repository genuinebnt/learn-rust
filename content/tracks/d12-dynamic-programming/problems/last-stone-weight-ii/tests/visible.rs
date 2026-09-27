use solution::*;

#[test]
fn leetcode_six() {
    check!(r#"stones = [2, 7, 4, 1, 8, 1]"#, last_stone_weight_ii(&[2, 7, 4, 1, 8, 1]), 1);
}

#[test]
fn leetcode_heaviest_first_fails() {
    check!(r#"stones = [31, 26, 33, 21, 40]"#, last_stone_weight_ii(&[31, 26, 33, 21, 40]), 5);
}

#[test]
fn no_stones() {
    check!(r#"stones = []"#, last_stone_weight_ii(&[]), 0);
}

#[test]
fn one_stone() {
    check!(r#"stones = [1]"#, last_stone_weight_ii(&[1]), 1);
}

#[test]
fn equal_pair() {
    check!(r#"stones = [5, 5]"#, last_stone_weight_ii(&[5, 5]), 0);
}
