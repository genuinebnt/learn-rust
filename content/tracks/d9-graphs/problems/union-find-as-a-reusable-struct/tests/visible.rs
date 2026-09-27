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

#[test]
fn pairs_then_join() {
    let mut uf = UnionFind::new(5);
    uf.union(0, 1);
    uf.union(2, 3);
    uf.union(1, 3);
    check!(r#"n = 5; union(0,1), union(2,3), union(1,3)"#, (uf.set_size(0), uf.set_count(), uf.connected(0, 3), uf.connected(0, 4)), (4, 2, true, false));
}

#[test]
fn union_with_itself() {
    let mut uf = UnionFind::new(2);
    check!(r#"n = 2; union(1, 1)"#, (uf.union(1, 1), uf.set_count(), uf.set_size(1)), (false, 2, 1));
}

#[test]
fn connected_to_itself() {
    let mut uf = UnionFind::new(4);
    check!(r#"n = 4; connected(3, 3)"#, (uf.connected(3, 3), uf.find(3)), (true, 3));
}
