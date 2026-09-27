use solution::*;

#[test]
fn root_itself() {
    check!(r#"parent = [0]; find(0)"#, find(&mut [0], 0), 0);
}

#[test]
fn mid_path() {
    let mut p = vec![1, 2, 2, 0];
    let root = find(&mut p, 3);
    check!(r#"parent = [1, 2, 2, 0]; find(3)"#, (root, p), (2, vec![2, 2, 2, 2]));
}
