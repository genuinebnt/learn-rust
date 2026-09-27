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

#[test]
fn root_has_no_parent() {
    let r = Node::root("r");
    check!(r#"a lone root r"#, (r.parent_name(), r.child_names()), (None, Vec::<String>::new()));
}

#[test]
fn children_in_order() {
    let r = Node::root("r");
    r.add_child("a");
    r.add_child("b");
    check!(r#"root r with children a, then b"#, r.child_names(), vec!["a".to_string(), "b".to_string()]);
}

#[test]
fn parent_keeps_children_alive() {
    let r = Node::root("r");
    let c = r.add_child("c");
    let w = std::rc::Rc::downgrade(&c);
    drop(c);
    check!(r#"root r with child c; drop the handle to c"#, (r.child_names(), w.upgrade().is_some()), (vec!["c".to_string()], true));
}
