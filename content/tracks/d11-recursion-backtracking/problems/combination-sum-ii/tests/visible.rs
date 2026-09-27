use solution::*;

fn norm<T: Ord>(mut groups: Vec<Vec<T>>) -> Vec<Vec<T>> {
    for g in &mut groups {
        g.sort();
    }
    groups.sort();
    groups
}

#[test]
fn leetcode_target_eight() {
    check!(r#"candidates = [10, 1, 2, 7, 6, 1, 5], target = 8"#, norm(combination_sum2(&[10, 1, 2, 7, 6, 1, 5], 8)), vec![vec![1, 1, 6], vec![1, 2, 5], vec![1, 7], vec![2, 6]]);
}

#[test]
fn leetcode_target_five() {
    check!(r#"candidates = [2, 5, 2, 1, 2], target = 5"#, norm(combination_sum2(&[2, 5, 2, 1, 2], 5)), vec![vec![1, 2, 2], vec![5]]);
}

#[test]
fn none() {
    check!(r#"candidates = [3], target = 2"#, combination_sum2(&[3], 2), Vec::<Vec<u32>>::new());
}

#[test]
fn each_used_once() {
    check!(r#"candidates = [2], target = 4"#, combination_sum2(&[2], 4), Vec::<Vec<u32>>::new());
}

#[test]
fn repeats_count_once() {
    check!(r#"candidates = [3, 3, 3, 3], target = 6"#, combination_sum2(&[3, 3, 3, 3], 6), vec![vec![3, 3]]);
}
