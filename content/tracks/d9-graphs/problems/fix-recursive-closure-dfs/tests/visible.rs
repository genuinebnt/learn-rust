use solution::*;

#[test]
fn partial() {
    check!(r#"adj = [[1], [2], [], [0]], start = 0"#, count_reachable(&[vec![1], vec![2], vec![], vec![0]], 0), 3);
}

#[test]
fn cycle() {
    check!(r#"adj = [[1], [0]], start = 1"#, count_reachable(&[vec![1], vec![0]], 1), 2);
}

#[test]
fn from_the_middle() {
    check!(r#"adj = [[1], [2], [3], []], start = 2"#, count_reachable(&[vec![1], vec![2], vec![3], vec![]], 2), 2);
}

#[test]
fn diamond_counts_once() {
    check!(r#"adj = [[1, 2], [3], [3], []], start = 0"#, count_reachable(&[vec![1, 2], vec![3], vec![3], vec![]], 0), 4);
}

#[test]
fn edges_are_directed() {
    check!(r#"adj = [[], [0]], start = 0"#, count_reachable(&[vec![], vec![0]], 0), 1);
}
