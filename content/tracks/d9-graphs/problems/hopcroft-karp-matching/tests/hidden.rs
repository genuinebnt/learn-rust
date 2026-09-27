use solution::*;

#[test]
fn no_edges() {
    check!(r#"left = 3, right = 2, edges = []"#, max_matching(3, 2, &[]), 0);
}

#[test]
fn perfect_ring() {
    let edges: Vec<(usize, usize)> = (0..5000).flat_map(|i| [(i, (i + 1) % 5000), (i, i)]).collect();
    check!(r#"5000 × 5000, i → i and i → i + 1"#, max_matching(5000, 5000, &edges), 5000);
}

#[test]
fn dense_block() {
    let edges: Vec<(usize, usize)> = (0..5000).flat_map(|i| (0..20).map(move |k| (i, (i * 7 + k * 251) % 5000))).collect();
    check!(r#"5000 × 5000, each left node to 20 right nodes"#, max_matching(5000, 5000, &edges), 5000);
}
