use solution::*;

#[test]
fn node_is_twelve_bytes() {
    check!(r#"size_of::<Node>()"#, std::mem::size_of::<Node>(), 12);
}

#[test]
fn insert_and_in_order() {
    let mut t = Tree::new();
    let r = [5, 3, 8, 3].map(|k| t.insert(k));
    check!(r#"insert 5, 3, 8, 3"#, (r, t.in_order()), ([true, true, true, false], vec![3, 5, 8]));
}

#[test]
fn contains() {
    let mut t = Tree::new();
    for k in [5, 3, 8] {
        t.insert(k);
    }
    check!(r#"insert 5, 3, 8; contains 3, 4, 8"#, (t.contains(3), t.contains(4), t.contains(8)), (true, false, true));
}

#[test]
fn links_are_options() {
    let mut t = Tree::new();
    t.insert(5);
    t.insert(3);
    check!(r#"insert 5, 3: root's right and the leaf's links"#, (t.nodes[0].left.is_some(), t.nodes[0].right.is_none(), t.nodes[1].left.is_none(), t.nodes[1].right.is_none()), (true, true, true, true));
}

#[test]
fn empty_tree() {
    let t = Tree::new();
    check!(r#"Tree::new()"#, (t.contains(0), t.in_order()), (false, Vec::<i32>::new()));
}
