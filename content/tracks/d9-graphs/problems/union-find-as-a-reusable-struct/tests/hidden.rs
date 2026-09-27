use solution::*;

#[test]
fn million_chain() {
    let mut uf = UnionFind::new(1_000_000);
    for i in 0..999_999 {
        uf.union(i, i + 1);
    }
    check!(r#"n = 10⁶; union(i, i + 1) for all i"#, (uf.set_count(), uf.connected(0, 999_999), uf.set_size(500_000)), (1, true, 1_000_000));
}

#[test]
fn self_union() {
    let mut uf = UnionFind::new(4);
    check!(r#"union(2, 2)"#, (uf.union(2, 2), uf.set_count()), (false, 4));
}
