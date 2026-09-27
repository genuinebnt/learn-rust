use solution::*;

#[test]
fn echo_in_background() {
    let mut bus = Bus::default();
    bus.register(Box::new(Echo { prefix: "> ".into() }));
    check!(r#"Echo "> ", events [a, b]"#, dispatch_in_background(bus, vec!["a".into(), "b".into()]), vec!["> a", "> b"]);
}

#[test]
fn counter_shared_with_caller() {
    let count = std::sync::Arc::new(std::sync::atomic::AtomicUsize::new(0));
    let mut bus = Bus::default();
    bus.register(Box::new(Counter { count: count.clone() }));
    dispatch_in_background(bus, vec!["x".into(), "y".into(), "z".into()]);
    check!(r#"Counter, three events in background, then read count"#, count.load(std::sync::atomic::Ordering::SeqCst), 3);
}

#[test]
fn dispatch_order() {
    let mut bus = Bus::default();
    bus.register(Box::new(Echo { prefix: "1".into() }));
    bus.register(Box::new(Echo { prefix: "2".into() }));
    check!(r#"Echo 1, Echo 2; events [a, b]"#, bus.dispatch(&["a", "b"]), vec!["1a", "2a", "1b", "2b"]);
}

#[test]
fn no_handlers() {
    check!(r#"empty bus"#, dispatch_in_background(Bus::default(), vec!["a".into()]), Vec::<String>::new());
}

#[test]
fn send_but_not_sync_handler() {
    // Cell is Send but not Sync: a bus that moves to one thread doesn't need Sync.
    struct Tally(std::cell::Cell<u32>);
    impl Handler for Tally {
        fn handle(&self, e: &str) -> Option<String> {
            self.0.set(self.0.get() + 1);
            Some(format!("{e}#{}", self.0.get()))
        }
    }
    let mut bus = Bus::default();
    bus.register(Box::new(Tally(std::cell::Cell::new(0))));
    check!("Tally, events [a, b]", dispatch_in_background(bus, vec!["a".into(), "b".into()]), vec!["a#1", "b#2"]);
}
