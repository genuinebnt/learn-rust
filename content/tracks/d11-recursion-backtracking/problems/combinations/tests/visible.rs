use solution::*;

fn norm<T: Ord>(mut groups: Vec<Vec<T>>) -> Vec<Vec<T>> {
    for g in &mut groups {
        g.sort();
    }
    groups.sort();
    groups
}

#[test]
fn leetcode_four_choose_two() {
    check!(r#"n = 4, k = 2"#, norm(combine(4, 2)), vec![vec![1, 2], vec![1, 3], vec![1, 4], vec![2, 3], vec![2, 4], vec![3, 4]]);
}

#[test]
fn leetcode_one_choose_one() {
    check!(r#"n = 1, k = 1"#, combine(1, 1), vec![vec![1]]);
}

#[test]
fn choose_zero() {
    check!(r#"n = 3, k = 0"#, combine(3, 0), vec![Vec::<u32>::new()]);
}

#[test]
fn choose_all() {
    check!(r#"n = 3, k = 3"#, norm(combine(3, 3)), vec![vec![1, 2, 3]]);
}

#[test]
fn no_repeats_no_reorders() {
    check!(r#"n = 3, k = 2"#, norm(combine(3, 2)), vec![vec![1, 2], vec![1, 3], vec![2, 3]]);
}
