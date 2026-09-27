use solution::*;

#[test]
fn links() {
    let r = Node::root("r");
    let c = r.add_child("c");
    check!(r#"root r with child c"#, (c.parent_name(), r.child_names()), (Some("r".to_string()), vec!["c".to_string()]));
}

#[test]
fn freed() {
    let r = Node::root("r");
    let c = r.add_child("c");
    let w = std::rc::Rc::downgrade(&r);
    drop(c);
    drop(r);
    check!(r#"drop the root and its child; is the root gone?"#, w.upgrade().is_none(), true);
}
