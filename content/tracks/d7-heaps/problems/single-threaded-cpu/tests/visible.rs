use solution::*;

#[test]
fn leetcode_one() {
    check!(r#"tasks = [(1, 2), (2, 4), (3, 2), (4, 1)]"#, get_order(&[(1, 2), (2, 4), (3, 2), (4, 1)]), vec![0, 2, 3, 1]);
}

#[test]
fn leetcode_same_arrival() {
    check!(r#"tasks = [(7, 10), (7, 12), (7, 5), (7, 4), (7, 2)]"#, get_order(&[(7, 10), (7, 12), (7, 5), (7, 4), (7, 2)]), vec![4, 3, 2, 0, 1]);
}

#[test]
fn empty() {
    check!(r#"tasks = []"#, get_order(&[]), Vec::<usize>::new());
}

#[test]
fn idle_until_the_next_arrival() {
    check!(r#"tasks = [(10, 1), (0, 1)]"#, get_order(&[(10, 1), (0, 1)]), vec![1, 0]);
}

#[test]
fn ties_by_index() {
    check!(r#"tasks = [(0, 5), (0, 5), (0, 5)]"#, get_order(&[(0, 5), (0, 5), (0, 5)]), vec![0, 1, 2]);
}

#[test]
fn arrival_at_finish_counts() {
    check!(r#"tasks = [(0, 2), (2, 1), (1, 3)] (at time 2 both 1 and 2 wait)"#, get_order(&[(0, 2), (2, 1), (1, 3)]), vec![0, 1, 2]);
}
