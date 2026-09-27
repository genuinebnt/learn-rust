use solution::*;

#[test]
fn leetcode_four() {
    check!(r#"intervals = [(1, 4), (2, 4), (3, 6), (4, 4)], queries = [2, 3, 4, 5]"#, min_interval(&[(1, 4), (2, 4), (3, 6), (4, 4)], &[2, 3, 4, 5]), vec![Some(3), Some(3), Some(1), Some(4)]);
}

#[test]
fn leetcode_with_miss() {
    check!(r#"intervals = [(2, 3), (2, 5), (1, 8), (20, 25)], queries = [2, 19, 5, 22]"#, min_interval(&[(2, 3), (2, 5), (1, 8), (20, 25)], &[2, 19, 5, 22]), vec![Some(2), None, Some(4), Some(6)]);
}

#[test]
fn no_intervals() {
    check!(r#"intervals = [], queries = [1]"#, min_interval(&[], &[1]), vec![None]);
}

#[test]
fn no_queries() {
    check!(r#"intervals = [(1, 2)], queries = []"#, min_interval(&[(1, 2)], &[]), Vec::<Option<u64>>::new());
}

#[test]
fn ends_are_included() {
    check!(r#"intervals = [(1, 1)], queries = [1]"#, min_interval(&[(1, 1)], &[1]), vec![Some(1)]);
}

#[test]
fn answers_in_query_order() {
    check!(r#"intervals = [(0, 10), (5, 6)], queries = [6, 0, 20]"#, min_interval(&[(0, 10), (5, 6)], &[6, 0, 20]), vec![Some(2), Some(11), None]);
}
