use solution::*;

#[test]
fn leetcode_example() {
    check!(r#"stones = [2, 7, 4, 1, 8, 1]"#, last_stone_weight(&[2, 7, 4, 1, 8, 1]), Some(1));
}

#[test]
fn leetcode_single() {
    check!(r#"stones = [1]"#, last_stone_weight(&[1]), Some(1));
}

#[test]
fn equal_pair_destroys_both() {
    check!(r#"stones = [3, 3]"#, last_stone_weight(&[3, 3]), None);
}

#[test]
fn empty() {
    check!(r#"stones = []"#, last_stone_weight(&[]), None);
}

#[test]
fn heaviest_two_first() {
    check!(r#"stones = [10, 4, 2, 10] (10 and 10 go first)"#, last_stone_weight(&[10, 4, 2, 10]), Some(2));
}

#[test]
fn no_zero_stone() {
    check!(r#"stones = [5, 5, 5, 5]"#, last_stone_weight(&[5, 5, 5, 5]), None);
}
