use solution::*;

#[test]
fn partial() {
    check!(r#"adj = [[1], [2], [], [0]], start = 0"#, count_reachable(&[vec![1], vec![2], vec![], vec![0]], 0), 3);
}

#[test]
fn cycle() {
    check!(r#"adj = [[1], [0]], start = 1"#, count_reachable(&[vec![1], vec![0]], 1), 2);
}
