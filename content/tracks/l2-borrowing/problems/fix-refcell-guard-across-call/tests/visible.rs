use solution::*;

#[test]
fn emit_in_order() {
    let bus = Bus::new();
    let seen = std::rc::Rc::new(std::cell::RefCell::new(Vec::new()));
    for k in 1..=2 {
        let seen = seen.clone();
        bus.subscribe(move |_, e| seen.borrow_mut().push(format!("{k}:{e}")));
    }
    bus.emit("x");
    check!(r#"two listeners logging "1:<e>" and "2:<e>" into a shared Vec; emit x"#, seen.borrow().clone(), vec!["1:x".to_string(), "2:x".to_string()]);
}

#[test]
fn subscribe_from_a_listener() {
    let bus = Bus::new();
    bus.subscribe(|b, e| {
        if e == "add" {
            b.subscribe(|b, e| if !e.starts_with("heard") { b.emit(&format!("heard {e}")) });
        }
    });
    bus.emit("add");
    bus.emit("ping");
    check!(r#"a listener that subscribes a logger on "add"; emit add, then ping"#, bus.log(), ["add", "ping", "heard ping"].map(String::from).to_vec());
}

#[test]
fn nested_emit() {
    let bus = Bus::new();
    bus.subscribe(|b, e| if e == "ping" { b.emit("pong") });
    bus.emit("ping");
    check!(r#"a listener that answers "ping" with "pong"; emit ping"#, bus.log(), ["ping", "pong"].map(String::from).to_vec());
}

#[test]
fn replay() {
    let bus = Bus::new();
    bus.emit("a");
    bus.emit("b");
    bus.replay();
    check!(r#"no listeners; emit a, b; replay"#, bus.log(), ["a", "b", "a", "b"].map(String::from).to_vec());
}

#[test]
fn replay_with_answers() {
    let bus = Bus::new();
    bus.subscribe(|b, e| if e == "ping" { b.emit("pong") });
    bus.emit("ping");
    bus.replay();
    check!(r#"ping -> pong listener; emit ping; replay"#, bus.log(), ["ping", "pong", "ping", "pong", "pong"].map(String::from).to_vec());
}
