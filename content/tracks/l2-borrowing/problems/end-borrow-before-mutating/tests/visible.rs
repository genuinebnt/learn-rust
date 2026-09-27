use solution::*;

#[test]
fn intern_all_example() {
    let mut i = Interner::new();
    let r = intern_all(&mut i, &["a", "b", "a"]);
    check!(r#"intern_all(["a", "b", "a"])"#, (r.clone(), r[0].as_ptr() == r[2].as_ptr()), (vec!["a", "b", "a"], true));
}

#[test]
fn intern_all_then_len() {
    let mut i = Interner::new();
    check!(r#"intern_all(["x", "x", "y"]), then len()"#, { intern_all(&mut i, &["x", "x", "y"]); i.len() }, 2);
}

#[test]
fn edges_example() {
    let mut i = Interner::new();
    let (pairs, added) = intern_edges(&mut i, &[("a", "b"), ("b", "c")]);
    check!(r#"intern_edges([("a", "b"), ("b", "c")])"#, (pairs.clone(), added, pairs[0].1.as_ptr() == pairs[1].0.as_ptr()), (vec![("a", "b"), ("b", "c")], 3, true));
}

#[test]
fn edges_counts_only_new_names() {
    let mut i = Interner::new();
    i.intern("a");
    let (pairs, added) = intern_edges(&mut i, &[("a", "z")]);
    check!(r#"intern "a" first, then intern_edges([("a", "z")])"#, (pairs, added), (vec![("a", "z")], 1));
}

#[test]
fn empty_inputs() {
    let mut i = Interner::new();
    check!(r#"intern_all([]), intern_edges([])"#, { let a = intern_all(&mut i, &[]).len(); let (p, n) = intern_edges(&mut i, &[]); (a, p.len(), n) }, (0, 0, 0));
}
