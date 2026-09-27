use solution::*;

#[test]
fn grandchild_freed() {
    let r = Node::root("r");
    let c = r.add_child("c");
    let g = c.add_child("g");
    let (wr, wg) = (std::rc::Rc::downgrade(&r), std::rc::Rc::downgrade(&g));
    drop(g);
    drop(c);
    drop(r);
    check!(r#"r → c → g; drop every handle"#, (wr.upgrade().is_none(), wg.upgrade().is_none()), (true, true));
}

#[test]
fn orphan() {
    let r = Node::root("r");
    let c = r.add_child("c");
    drop(r);
    check!(r#"keep the child, drop the root"#, c.parent_name(), None);
}
