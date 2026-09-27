use solution::*;

#[test]
fn independent() {
    let a = node(1);
    let b = node(2);
    link(&a, &b);
    let c = clone_graph(&a);
    c.borrow_mut().val = 9;
    let v = a.borrow().val;
    check!(r#"1-2; clone, set copy's val to 9; original val"#, v, 1);
}

#[test]
fn self_loop() {
    let a = node(1);
    link(&a, &a);
    let c = clone_graph(&a);
    let first = std::rc::Rc::clone(&c.borrow().neighbors[0]);
    let same = std::rc::Rc::ptr_eq(&first, &c) && c.borrow().neighbors.len() == 2;
    check!(r#"1 linked to itself"#, same, true);
}

#[test]
fn lonely() {
    let c = clone_graph(&node(7));
    let n = (c.borrow().val, c.borrow().neighbors.len());
    check!(r#"a single node"#, n, (7, 0));
}
