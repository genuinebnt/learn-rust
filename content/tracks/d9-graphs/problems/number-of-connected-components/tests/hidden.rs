use solution::*;

#[test]
fn isolated() {
    check!(r#"n = 3, edges = []"#, count_components(3, &[]), 3);
}

#[test]
fn million() {
    let edges: Vec<(usize, usize)> = (0..500_000).map(|i| (2 * i, 2 * i + 1)).collect();
    check!(r#"n = 10⁶, edges pair up neighbours (0-1, 2-3, …)"#, count_components(1_000_000, &edges), 500_000);
}

#[test]
fn long_chain() {
    let edges: Vec<(usize, usize)> = (1..1_000_000).map(|i| (i, i - 1)).collect();
    check!(r#"n = 10⁶, chain"#, count_components(1_000_000, &edges), 1);
}
