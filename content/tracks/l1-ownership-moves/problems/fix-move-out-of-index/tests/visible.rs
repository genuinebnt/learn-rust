use solution::*;

#[test]
fn take_first_keeps_positions() {
    let mut q = Queue::new("q", vec!["a".to_string(), "b".to_string()]);
    check!(r#"items ["a", "b"], take_first"#, (q.take_first(), q.items), ("a".to_string(), vec!["".to_string(), "b".to_string()]));
}

#[test]
fn start_next_twice() {
    let mut q = Queue::new("q", vec!["a".to_string(), "b".to_string()]);
    check!(r#"items ["a", "b"], start_next twice"#, (q.start_next(), q.start_next(), q.current), (None, Some("b".to_string()), Some("a".to_string())));
}

#[test]
fn finish_moves_to_done() {
    let mut q = Queue::new("q", vec!["x".to_string()]);
    q.start_next();
    check!(r#"start_next, finish, finish"#, (q.finish(), q.finish(), q.current, q.done), (true, false, None, vec!["x".to_string()]));
}

#[test]
fn drain_done_empties() {
    let mut q = Queue::new("q", vec!["a".to_string(), "b".to_string()]);
    for _ in 0..2 {
        q.start_next();
        q.finish();
    }
    check!(r#"finish two jobs, drain_done, drain_done"#, (q.drain_done(), q.drain_done()), (vec!["b".to_string(), "a".to_string()], Vec::<String>::new()));
}

#[test]
fn swap_items_only() {
    let mut p = Queue::new("p", vec!["a".to_string(), "c".to_string()]);
    p.start_next();
    let mut o = Queue::new("o", vec!["x".to_string(), "y".to_string()]);
    p.swap_items(&mut o);
    check!(r#"swap_items between ["a"] (current "c") and ["x", "y"]"#, (p.items, p.current, o.items, o.name), (vec!["x".to_string(), "y".to_string()], Some("c".to_string()), vec!["a".to_string()], "o".to_string()));
}
