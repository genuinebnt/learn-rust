use solution::*;

#[test]
fn three() {
    check!(r#"nums = [1, 2, 1]"#, concat_twice(&[1, 2, 1]), vec![1, 2, 1, 1, 2, 1]);
}

#[test]
fn empty() {
    check!(r#"nums = []"#, concat_twice(&[]), Vec::<i32>::new());
}

#[test]
fn single() {
    check!(r#"nums = [5]"#, concat_twice(&[5]), vec![5, 5]);
}

#[test]
fn order_kept() {
    check!(r#"nums = [3, 1, 2]"#, concat_twice(&[3, 1, 2]), vec![3, 1, 2, 3, 1, 2]);
}

#[test]
fn negatives() {
    check!(r#"nums = [-1, 0]"#, concat_twice(&[-1, 0]), vec![-1, 0, -1, 0]);
}

#[test]
fn leetcode_four() {
    check!(r#"nums = [1, 3, 2, 1]"#, concat_twice(&[1, 3, 2, 1]), vec![1, 3, 2, 1, 1, 3, 2, 1]);
}
