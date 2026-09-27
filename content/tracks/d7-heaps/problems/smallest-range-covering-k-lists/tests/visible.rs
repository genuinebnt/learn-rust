use solution::*;

#[test]
fn leetcode_one() {
    check!(r#"lists = [[4, 10, 15, 24, 26], [0, 9, 12, 20], [5, 18, 22, 30]]"#, smallest_range(&[vec![4, 10, 15, 24, 26], vec![0, 9, 12, 20], vec![5, 18, 22, 30]]), Some((20, 24)));
}

#[test]
fn leetcode_same_lists() {
    check!(r#"lists = [[1, 2, 3], [1, 2, 3], [1, 2, 3]]"#, smallest_range(&[vec![1, 2, 3], vec![1, 2, 3], vec![1, 2, 3]]), Some((1, 1)));
}

#[test]
fn single_list() {
    check!(r#"lists = [[5, 8]]"#, smallest_range(&[vec![5, 8]]), Some((5, 5)));
}

#[test]
fn equal_widths_take_smaller_start() {
    check!(r#"lists = [[1, 10], [4, 13]] ((1, 4) and (10, 13) both have width 3)"#, smallest_range(&[vec![1, 10], vec![4, 13]]), Some((1, 4)));
}

#[test]
fn no_lists() {
    check!(r#"lists = []"#, smallest_range(&[]), None);
}

#[test]
fn an_empty_list() {
    check!(r#"lists = [[1, 2], []]"#, smallest_range(&[vec![1, 2], vec![]]), None);
}
