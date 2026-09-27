use solution::*;

#[test]
fn leetcode_one() {
    check!(r#"intervals = [(1, 2), (2, 3), (3, 4), (1, 3)]"#, erase_overlap_intervals(&[(1, 2), (2, 3), (3, 4), (1, 3)]), 1);
}

#[test]
fn leetcode_copies() {
    check!(r#"intervals = [(1, 2), (1, 2), (1, 2)]"#, erase_overlap_intervals(&[(1, 2), (1, 2), (1, 2)]), 2);
}

#[test]
fn leetcode_touching() {
    check!(r#"intervals = [(1, 2), (2, 3)]"#, erase_overlap_intervals(&[(1, 2), (2, 3)]), 0);
}

#[test]
fn empty() {
    check!(r#"intervals = []"#, erase_overlap_intervals(&[]), 0);
}

#[test]
fn single() {
    check!(r#"intervals = [(4, 9)]"#, erase_overlap_intervals(&[(4, 9)]), 0);
}

#[test]
fn drop_the_long_one() {
    check!(r#"intervals = [(1, 100), (1, 2), (3, 4), (5, 6)]"#, erase_overlap_intervals(&[(1, 100), (1, 2), (3, 4), (5, 6)]), 1);
}
