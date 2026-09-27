use solution::*;

#[test]
fn leetcode_mixed() {
    check!(r#"a = [(0, 2), (5, 10), (13, 23), (24, 25)], b = [(1, 5), (8, 12), (15, 24), (25, 26)]"#, interval_intersection(&[(0, 2), (5, 10), (13, 23), (24, 25)], &[(1, 5), (8, 12), (15, 24), (25, 26)]), vec![(1, 2), (5, 5), (8, 10), (15, 23), (24, 24), (25, 25)]);
}

#[test]
fn leetcode_one_empty() {
    check!(r#"a = [(1, 3), (5, 9)], b = []"#, interval_intersection(&[(1, 3), (5, 9)], &[]), Vec::<(i32, i32)>::new());
}

#[test]
fn both_empty() {
    check!(r#"a = [], b = []"#, interval_intersection(&[], &[]), Vec::<(i32, i32)>::new());
}

#[test]
fn shared_point() {
    check!(r#"a = [(1, 5)], b = [(5, 8)]"#, interval_intersection(&[(1, 5)], &[(5, 8)]), vec![(5, 5)]);
}

#[test]
fn one_covers_many() {
    check!(r#"a = [(0, 10)], b = [(1, 2), (4, 5)]"#, interval_intersection(&[(0, 10)], &[(1, 2), (4, 5)]), vec![(1, 2), (4, 5)]);
}

#[test]
fn no_overlap() {
    check!(r#"a = [(1, 2)], b = [(3, 4)]"#, interval_intersection(&[(1, 2)], &[(3, 4)]), Vec::<(i32, i32)>::new());
}
