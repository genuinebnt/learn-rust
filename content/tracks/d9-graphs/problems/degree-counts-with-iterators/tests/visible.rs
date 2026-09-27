use solution::*;

#[test]
fn triangle() {
    check!(r#"n = 3, edges = [(0, 1), (0, 2), (1, 2)]"#, (degrees(3, &[(0, 1), (0, 2), (1, 2)]), sources(3, &[(0, 1), (0, 2), (1, 2)])), (vec![(0, 2), (1, 1), (2, 0)], vec![0]));
}

#[test]
fn isolated() {
    check!(r#"n = 2, edges = []"#, (degrees(2, &[]), sources(2, &[])), (vec![(0, 0), (0, 0)], vec![0, 1]));
}

#[test]
fn fan_in() {
    check!(r#"n = 3, edges = [(0, 2), (1, 2)]"#, (degrees(3, &[(0, 2), (1, 2)]), sources(3, &[(0, 2), (1, 2)])), (vec![(0, 1), (0, 1), (2, 0)], vec![0, 1]));
}

#[test]
fn parallel_edges_count_twice() {
    check!(r#"n = 2, edges = [(1, 0), (1, 0)]"#, (degrees(2, &[(1, 0), (1, 0)]), sources(2, &[(1, 0), (1, 0)])), (vec![(2, 0), (0, 2)], vec![1]));
}

#[test]
fn self_loop_counts_both_ways() {
    check!(r#"n = 2, edges = [(1, 1)]"#, (degrees(2, &[(1, 1)]), sources(2, &[(1, 1)])), (vec![(0, 0), (1, 1)], vec![0]));
}
