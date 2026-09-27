use solution::*;

#[test]
fn merges() {
    let mut uf = UnionFind::new(5);
    let first = uf.union(0, 1);
    uf.union(1, 2);
    let again = uf.union(0, 2);
    check!(r#"n = 5; union(0,1), union(1,2), union(0,2)"#, (first, again, uf.connected(0, 2), uf.connected(0, 3), uf.set_count(), uf.set_size(2)), (true, false, true, false, 3, 3));
}

#[test]
fn fresh() {
    let mut uf = UnionFind::new(3);
    check!(r#"n = 3"#, (uf.set_count(), uf.set_size(1), uf.find(2)), (3, 1, 2));
}
