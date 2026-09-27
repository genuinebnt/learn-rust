use solution::*;

#[test]
fn compresses() {
    let mut p = vec![1, 2, 3, 3];
    let root = find(&mut p, 0);
    check!(r#"parent = [1, 2, 3, 3]; find(0)"#, (root, p), (3, vec![3, 3, 3, 3]));
}

#[test]
fn unions() {
    let mut p: Vec<usize> = (0..4).collect();
    let (a, b, c, d) = (union(&mut p, 0, 1), union(&mut p, 2, 3), union(&mut p, 1, 3), union(&mut p, 0, 2));
    check!(r#"4 singletons; union(0,1), union(2,3), union(1,3), union(0,2)"#, (a, b, c, d), (true, true, true, false));
}
