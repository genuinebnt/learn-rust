use solution::*;

fn norm<T: Ord>(mut groups: Vec<Vec<T>>) -> Vec<Vec<T>> {
    for g in &mut groups {
        g.sort();
    }
    groups.sort();
    groups
}

#[test]
fn leetcode_three() {
    check!(r#"nums = [1, 2, 3]"#, norm(subsets(&[1, 2, 3])), norm(vec![vec![], vec![1], vec![2], vec![1, 2], vec![3], vec![1, 3], vec![2, 3], vec![1, 2, 3]]));
}

#[test]
fn leetcode_single() {
    check!(r#"nums = [0]"#, norm(subsets(&[0])), vec![vec![], vec![0]]);
}

#[test]
fn empty_has_one_subset() {
    check!(r#"nums = []"#, subsets(&[]), vec![Vec::<i32>::new()]);
}

#[test]
fn negatives() {
    check!(r#"nums = [-1, 2]"#, norm(subsets(&[-1, 2])), vec![vec![], vec![-1], vec![-1, 2], vec![2]]);
}

#[test]
fn five_values_give_32() {
    check!(r#"nums = [1, 2, 3, 4, 5]"#, subsets(&[1, 2, 3, 4, 5]).len(), 32);
}
