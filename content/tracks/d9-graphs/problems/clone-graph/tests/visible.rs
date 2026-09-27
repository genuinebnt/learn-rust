use solution::*;

#[test]
fn four_cycle() {
    let n: Vec<NodeRef> = (1..=4).map(node).collect();
    link(&n[0], &n[1]);
    link(&n[1], &n[2]);
    link(&n[2], &n[3]);
    link(&n[3], &n[0]);
    let c = clone_graph(&n[0]);
    let vals: Vec<i32> = c.borrow().neighbors.iter().map(|x| x.borrow().val).collect();
    let fresh = !n.iter().any(|x| std::rc::Rc::ptr_eq(x, &c));
    check!(r#"1-2-3-4-1; clone from 1"#, (vals, fresh), (vec![2, 4], true));
}

#[test]
fn back_edge_is_shared() {
    let a = node(1);
    let b = node(2);
    link(&a, &b);
    let c = clone_graph(&a);
    let c2 = std::rc::Rc::clone(&c.borrow().neighbors[0]);
    let back = std::rc::Rc::clone(&c2.borrow().neighbors[0]);
    let same = std::rc::Rc::ptr_eq(&back, &c);
    check!(r#"1-2; clone 1, follow 1 → 2 → 1"#, same, true);
}
