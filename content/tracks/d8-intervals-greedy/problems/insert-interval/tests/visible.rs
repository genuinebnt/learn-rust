use solution::*;

#[test]
fn leetcode_one_overlap() {
    check!(r#"intervals = [(1, 3), (6, 9)], new = (2, 5)"#, insert(&[(1, 3), (6, 9)], (2, 5)), vec![(1, 5), (6, 9)]);
}

#[test]
fn leetcode_three_overlaps() {
    check!(r#"intervals = [(1, 2), (3, 5), (6, 7), (8, 10), (12, 16)], new = (4, 8)"#, insert(&[(1, 2), (3, 5), (6, 7), (8, 10), (12, 16)], (4, 8)), vec![(1, 2), (3, 10), (12, 16)]);
}

#[test]
fn into_empty() {
    check!(r#"intervals = [], new = (5, 7)"#, insert(&[], (5, 7)), vec![(5, 7)]);
}

#[test]
fn goes_last() {
    check!(r#"intervals = [(1, 2)], new = (5, 6)"#, insert(&[(1, 2)], (5, 6)), vec![(1, 2), (5, 6)]);
}

#[test]
fn goes_first() {
    check!(r#"intervals = [(5, 6)], new = (1, 2)"#, insert(&[(5, 6)], (1, 2)), vec![(1, 2), (5, 6)]);
}

#[test]
fn touching_merges() {
    check!(r#"intervals = [(1, 3)], new = (3, 4)"#, insert(&[(1, 3)], (3, 4)), vec![(1, 4)]);
}
