use solution::*;

#[test]
fn leetcode_four() {
    check!(r#"nums = [5, 2, 3, 1]"#, merge_sort(&[5, 2, 3, 1]), vec![1, 2, 3, 5]);
}

#[test]
fn leetcode_duplicates() {
    check!(r#"nums = [5, 1, 1, 2, 0, 0]"#, merge_sort(&[5, 1, 1, 2, 0, 0]), vec![0, 0, 1, 1, 2, 5]);
}

#[test]
fn empty() {
    check!(r#"nums = []"#, merge_sort(&[]), Vec::<i32>::new());
}

#[test]
fn single() {
    check!(r#"nums = [7]"#, merge_sort(&[7]), vec![7]);
}

#[test]
fn negatives() {
    check!(r#"nums = [3, -1, 3, -8]"#, merge_sort(&[3, -1, 3, -8]), vec![-8, -1, 3, 3]);
}

#[test]
fn already_sorted() {
    check!(r#"nums = [1, 2, 3]"#, merge_sort(&[1, 2, 3]), vec![1, 2, 3]);
}
