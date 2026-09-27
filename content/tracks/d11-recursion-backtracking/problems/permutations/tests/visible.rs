use solution::*;

fn sorted<T: Ord>(mut v: Vec<T>) -> Vec<T> {
    v.sort();
    v
}

#[test]
fn leetcode_three() {
    check!(r#"nums = [1, 2, 3]"#, sorted(permute(&[1, 2, 3])), vec![vec![1, 2, 3], vec![1, 3, 2], vec![2, 1, 3], vec![2, 3, 1], vec![3, 1, 2], vec![3, 2, 1]]);
}

#[test]
fn leetcode_two() {
    check!(r#"nums = [0, 1]"#, sorted(permute(&[0, 1])), vec![vec![0, 1], vec![1, 0]]);
}

#[test]
fn leetcode_single() {
    check!(r#"nums = [1]"#, permute(&[1]), vec![vec![1]]);
}

#[test]
fn empty_has_one_ordering() {
    check!(r#"nums = []"#, permute(&[]), vec![Vec::<i32>::new()]);
}

#[test]
fn five_values_give_120() {
    check!(r#"nums = [1, 2, 3, 4, 5]"#, permute(&[1, 2, 3, 4, 5]).len(), 120);
}
