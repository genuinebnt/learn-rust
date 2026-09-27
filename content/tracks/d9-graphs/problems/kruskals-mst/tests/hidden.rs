use solution::*;

#[test]
fn single() {
    check!(r#"n = 1, edges = []"#, mst_weight(1, &[]), Some(0));
}

#[test]
fn parallel_edges() {
    check!(r#"n = 2, edges = [(0,1,9), (1,0,4)]"#, mst_weight(2, &[(0, 1, 9), (1, 0, 4)]), Some(4));
}

#[test]
fn big_weights() {
    check!(r#"n = 3, edges with weight 10¹²"#, mst_weight(3, &[(0, 1, 1_000_000_000_000), (1, 2, 1_000_000_000_000)]), Some(2_000_000_000_000));
}
