use solution::*;

fn norm<T: Ord>(mut groups: Vec<Vec<T>>) -> Vec<Vec<T>> {
    for g in &mut groups {
        g.sort();
    }
    groups.sort();
    groups
}

#[test]
fn leetcode_seven() {
    check!(r#"candidates = [2, 3, 6, 7], target = 7"#, norm(combination_sum(&[2, 3, 6, 7], 7)), vec![vec![2, 2, 3], vec![7]]);
}

#[test]
fn leetcode_eight() {
    check!(r#"candidates = [2, 3, 5], target = 8"#, norm(combination_sum(&[2, 3, 5], 8)), vec![vec![2, 2, 2, 2], vec![2, 3, 3], vec![3, 5]]);
}

#[test]
fn leetcode_none() {
    check!(r#"candidates = [2], target = 1"#, combination_sum(&[2], 1), Vec::<Vec<u32>>::new());
}

#[test]
fn reuse_one_value() {
    check!(r#"candidates = [3], target = 9"#, combination_sum(&[3], 9), vec![vec![3, 3, 3]]);
}

#[test]
fn order_does_not_matter() {
    check!(r#"candidates = [1, 2], target = 4"#, norm(combination_sum(&[1, 2], 4)), vec![vec![1, 1, 1, 1], vec![1, 1, 2], vec![2, 2]]);
}
