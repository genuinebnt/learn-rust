use solution::*;

fn sorted<T: Ord>(mut v: Vec<T>) -> Vec<T> {
    v.sort();
    v
}

#[test]
fn leetcode_one_one_two() {
    check!(r#"nums = [1, 1, 2]"#, sorted(permute_unique(&[1, 1, 2])), vec![vec![1, 1, 2], vec![1, 2, 1], vec![2, 1, 1]]);
}

#[test]
fn leetcode_distinct() {
    check!(r#"nums = [1, 2, 3]"#, sorted(permute_unique(&[1, 2, 3])), vec![vec![1, 2, 3], vec![1, 3, 2], vec![2, 1, 3], vec![2, 3, 1], vec![3, 1, 2], vec![3, 2, 1]]);
}

#[test]
fn empty() {
    check!(r#"nums = []"#, permute_unique(&[]), vec![Vec::<i32>::new()]);
}

#[test]
fn all_equal() {
    check!(r#"nums = [2, 2, 2]"#, permute_unique(&[2, 2, 2]), vec![vec![2, 2, 2]]);
}

#[test]
fn duplicates_not_adjacent() {
    check!(r#"nums = [3, 1, 3]"#, sorted(permute_unique(&[3, 1, 3])), vec![vec![1, 3, 3], vec![3, 1, 3], vec![3, 3, 1]]);
}
