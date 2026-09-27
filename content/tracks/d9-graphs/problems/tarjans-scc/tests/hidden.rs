use solution::*;

#[test]
fn self_loop() {
    check!(r#"adj = [[0]]"#, strongly_connected(&[vec![0]]), vec![vec![0]]);
}

#[test]
fn back_to_earlier_scc() {
    check!(r#"adj = [[1], [0], [0, 3], [2]]"#, strongly_connected(&[vec![1], vec![0], vec![0, 3], vec![2]]), vec![vec![0, 1], vec![2, 3]]);
}

#[test]
fn big_cycle() {
    let adj: Vec<Vec<usize>> = (0..5000).map(|i| vec![(i + 1) % 5000]).collect();
    let out = strongly_connected(&adj);
    check!(r#"one cycle of 5000 nodes"#, (out.len(), out[0].len()), (1, 5000));
}
