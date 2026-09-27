use solution::*;

#[test]
fn no_events() {
    let mut bus = Bus::default();
    bus.register(Box::new(Echo { prefix: "!".into() }));
    check!(r#"Echo, no events"#, dispatch_in_background(bus, vec![]), Vec::<String>::new());
}

#[test]
fn counter_skipped_in_replies() {
    let count = std::sync::Arc::new(std::sync::atomic::AtomicUsize::new(0));
    let mut bus = Bus::default();
    bus.register(Box::new(Counter { count }));
    bus.register(Box::new(Echo { prefix: "~".into() }));
    check!(r#"Counter then Echo; events [e]"#, bus.dispatch(&["e"]), vec!["~e"]);
}

#[test]
fn counter_zero_events() {
    let count = std::sync::Arc::new(std::sync::atomic::AtomicUsize::new(0));
    let mut bus = Bus::default();
    bus.register(Box::new(Counter { count: count.clone() }));
    dispatch_in_background(bus, vec![]);
    check!(r#"Counter, no events"#, count.load(std::sync::atomic::Ordering::SeqCst), 0);
}

#[test]
fn two_counters_one_count() {
    let count = std::sync::Arc::new(std::sync::atomic::AtomicUsize::new(0));
    let mut bus = Bus::default();
    bus.register(Box::new(Counter { count: count.clone() }));
    bus.register(Box::new(Counter { count: count.clone() }));
    dispatch_in_background(bus, vec!["a".into(), "b".into()]);
    check!(r#"two Counters sharing one count, two events"#, count.load(std::sync::atomic::Ordering::SeqCst), 4);
}

#[test]
fn unicode_events() {
    let mut bus = Bus::default();
    bus.register(Box::new(Echo { prefix: "» ".into() }));
    check!(r#"Echo "» ", events [é, 日本]"#, dispatch_in_background(bus, vec!["é".into(), "日本".into()]), vec!["» é", "» 日本"]);
}

#[test]
fn dispatch_on_this_thread_too() {
    let mut bus = Bus::default();
    bus.register(Box::new(Echo { prefix: "-".into() }));
    check!(r#"Echo, dispatch(&[q])"#, bus.dispatch(&["q"]), vec!["-q"]);
}

#[test]
fn bus_is_send() {
    fn assert_send<T: Send>(_: &T) {}
    let bus = Bus::default();
    assert_send(&bus);
    check!("Bus is Send", true, true);
}

#[test]
fn handler_with_non_static_free_data() {
    // A handler owning a Vec, moved to the worker with the bus.
    struct Replies(Vec<&'static str>);
    impl Handler for Replies {
        fn handle(&self, e: &str) -> Option<String> {
            self.0.iter().find(|r| r.starts_with(e)).map(|r| r.to_string())
        }
    }
    let mut bus = Bus::default();
    bus.register(Box::new(Replies(vec!["hi there", "bye now"])));
    check!("Replies, events [bye, hi, x]", dispatch_in_background(bus, vec!["bye".into(), "hi".into(), "x".into()]), vec!["bye now", "hi there"]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(4408);
    for _ in 0..200 {
        let hn = rng.below(4);
        let prefixes: Vec<String> = (0..hn).map(|_| { let len = rng.below(3); rng.string(len, "pq") }).collect();
        let en = rng.below(4);
        let events: Vec<String> = (0..en).map(|_| { let len = rng.below(3); rng.string(len, "ab") }).collect();
        let count = std::sync::Arc::new(std::sync::atomic::AtomicUsize::new(0));
        let mut bus = Bus::default();
        bus.register(Box::new(Counter { count: count.clone() }));
        for p in &prefixes {
            bus.register(Box::new(Echo { prefix: p.clone() }));
        }
        let mut want = Vec::new();
        for e in &events {
            for p in &prefixes {
                want.push(format!("{p}{e}"));
            }
        }
        check!(format!("prefixes = {prefixes:?}, events = {events:?}"), dispatch_in_background(bus, events.clone()), want);
        check!(format!("count after {events:?}"), count.load(std::sync::atomic::Ordering::SeqCst), events.len());
    }
}
