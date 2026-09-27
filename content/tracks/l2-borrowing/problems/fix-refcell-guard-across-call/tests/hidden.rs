use solution::*;

#[test]
fn no_events() {
    let bus = Bus::new();
    bus.replay();
    check!(r#"new bus; replay"#, bus.log().len(), 0);
}

#[test]
fn nested_reaches_all_listeners() {
    let bus = Bus::new();
    let seen = std::rc::Rc::new(std::cell::RefCell::new(Vec::new()));
    bus.subscribe(|b, e| if e == "a" { b.emit("b") });
    let s2 = seen.clone();
    bus.subscribe(move |_, e| s2.borrow_mut().push(e.to_string()));
    bus.emit("a");
    check!(r#"listener 1 answers a with b; listener 2 records everything; emit a"#, seen.borrow().clone(), vec!["b".to_string(), "a".to_string()]);
}

#[test]
fn new_listener_misses_current_event() {
    let bus = Bus::new();
    let count = std::rc::Rc::new(std::cell::Cell::new(0));
    let c = count.clone();
    bus.subscribe(move |b, _| {
        let c = c.clone();
        b.subscribe(move |_, _| c.set(c.get() + 1));
    });
    bus.emit("x");
    bus.emit("y");
    check!(r#"listener subscribes a counter on every event; emit x, y"#, count.get(), 1);
}

#[test]
fn chain() {
    let bus = Bus::new();
    bus.subscribe(|b, e| if e == "a" { b.emit("b") });
    bus.subscribe(|b, e| if e == "b" { b.emit("c") });
    bus.emit("a");
    check!(r#"listeners: a -> b, b -> c; emit a"#, bus.log(), ["a", "b", "c"].map(String::from).to_vec());
}

#[test]
fn depth_first() {
    let bus = Bus::new();
    bus.subscribe(|b, e| match e { "a" => b.emit("b"), "b" => b.emit("d"), _ => {} });
    bus.subscribe(|b, e| if e == "a" { b.emit("c") });
    bus.emit("a");
    check!(r#"a -> [b, c] from two listeners, b -> d; emit a"#, bus.log(), ["a", "b", "d", "c"].map(String::from).to_vec());
}

#[test]
fn replay_twice() {
    let bus = Bus::new();
    bus.emit("a");
    bus.replay();
    bus.replay();
    check!(r#"emit a; replay; replay"#, bus.log(), ["a", "a", "a", "a"].map(String::from).to_vec());
}

#[test]
fn replay_from_a_listener() {
    let bus = Bus::new();
    let done = std::rc::Rc::new(std::cell::Cell::new(false));
    let d = done.clone();
    bus.subscribe(move |b, e| if e == "again" && !d.get() {
        d.set(true);
        b.replay();
    });
    bus.emit("x");
    bus.emit("again");
    check!(r#"a listener that replays on "again" (once); emit x, again"#, bus.log(), ["x", "again", "x", "again"].map(String::from).to_vec());
}

#[test]
fn unicode_events() {
    let bus = Bus::new();
    bus.emit("日本");
    bus.replay();
    check!(r#"emit 日本; replay"#, bus.log(), ["日本", "日本"].map(String::from).to_vec());
}

#[test]
fn many_listeners() {
    let bus = Bus::new();
    let hits = std::rc::Rc::new(std::cell::Cell::new(0u64));
    for _ in 0..1000 {
        let h = hits.clone();
        bus.subscribe(move |_, _| h.set(h.get() + 1));
    }
    for i in 0..100 {
        bus.emit(&i.to_string());
    }
    check!("1000 listeners, 100 events", (hits.get(), bus.log().len()), (100_000, 100));
}
