use solution::*;

fn norm<T: Ord>(mut groups: Vec<Vec<T>>) -> Vec<Vec<T>> {
    for g in &mut groups {
        g.sort();
    }
    groups.sort();
    groups
}

#[test]
fn leetcode_one_two_two() {
    check!(r#"nums = [1, 2, 2]"#, norm(subsets_with_dup(&[1, 2, 2])), vec![vec![], vec![1], vec![1, 2], vec![1, 2, 2], vec![2], vec![2, 2]]);
}

#[test]
fn leetcode_single() {
    check!(r#"nums = [0]"#, norm(subsets_with_dup(&[0])), vec![vec![], vec![0]]);
}

#[test]
fn empty() {
    check!(r#"nums = []"#, subsets_with_dup(&[]), vec![Vec::<i32>::new()]);
}

#[test]
fn all_equal() {
    check!(r#"nums = [2, 2, 2]"#, norm(subsets_with_dup(&[2, 2, 2])), vec![vec![], vec![2], vec![2, 2], vec![2, 2, 2]]);
}

#[test]
fn duplicates_not_adjacent() {
    check!(r#"nums = [4, 4, 1, 4]"#, norm(subsets_with_dup(&[4, 4, 1, 4])), vec![vec![], vec![1], vec![1, 4], vec![1, 4, 4], vec![1, 4, 4, 4], vec![4], vec![4, 4], vec![4, 4, 4]]);
}
