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

#[test]
fn single_node() {
    let a = node(1);
    let c = clone_graph(&a);
    check!(r#"a single node 1 with no neighbours"#, (c.borrow().val, c.borrow().neighbors.len(), std::rc::Rc::ptr_eq(&a, &c)), (1, 0, false));
}

#[test]
fn neighbour_order_kept() {
    let n: Vec<NodeRef> = (1..=4).map(node).collect();
    link(&n[0], &n[2]);
    link(&n[0], &n[1]);
    link(&n[0], &n[3]);
    let c = clone_graph(&n[0]);
    let vals: Vec<i32> = c.borrow().neighbors.iter().map(|x| x.borrow().val).collect();
    check!(r#"1 linked to 3, then 2, then 4; clone 1"#, vals, vec![3, 2, 4]);
}

#[test]
fn equal_values_are_different_nodes() {
    let a = node(5);
    let b = node(5);
    link(&a, &b);
    let c = clone_graph(&a);
    let first = std::rc::Rc::clone(&c.borrow().neighbors[0]);
    let first_is_other_node = !std::rc::Rc::ptr_eq(&first, &c);
    let back = std::rc::Rc::clone(&first.borrow().neighbors[0]);
    let back_is_start = std::rc::Rc::ptr_eq(&back, &c);
    check!(r#"two nodes both valued 5, linked; clone one"#, (first_is_other_node, back_is_start), (true, true));
}
