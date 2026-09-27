use solution::*;

#[test]
fn alone() {
    check!(r#"adj = [[]], start = 0"#, count_reachable(&[vec![]], 0), 1);
}

#[test]
fn self_loop() {
    check!(r#"adj = [[0], []], start = 0"#, count_reachable(&[vec![0], vec![]], 0), 1);
}
