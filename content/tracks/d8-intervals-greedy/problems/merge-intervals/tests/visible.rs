use solution::*;

#[test]
fn leetcode_four() {
    check!(r#"intervals = [(1, 3), (2, 6), (8, 10), (15, 18)]"#, merge(&[(1, 3), (2, 6), (8, 10), (15, 18)]), vec![(1, 6), (8, 10), (15, 18)]);
}

#[test]
fn leetcode_touching() {
    check!(r#"intervals = [(1, 4), (4, 5)]"#, merge(&[(1, 4), (4, 5)]), vec![(1, 5)]);
}

#[test]
fn leetcode_unsorted() {
    check!(r#"intervals = [(4, 7), (1, 4)]"#, merge(&[(4, 7), (1, 4)]), vec![(1, 7)]);
}

#[test]
fn empty() {
    check!(r#"intervals = []"#, merge(&[]), Vec::<(i32, i32)>::new());
}

#[test]
fn single() {
    check!(r#"intervals = [(2, 3)]"#, merge(&[(2, 3)]), vec![(2, 3)]);
}

#[test]
fn contained() {
    check!(r#"intervals = [(1, 10), (2, 3)]"#, merge(&[(1, 10), (2, 3)]), vec![(1, 10)]);
}

#[test]
fn output_sorted() {
    check!(r#"intervals = [(8, 10), (1, 3), (2, 6)]"#, merge(&[(8, 10), (1, 3), (2, 6)]), vec![(1, 6), (8, 10)]);
}
