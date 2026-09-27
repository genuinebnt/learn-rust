use solution::*;

#[test]
fn start_when_idle() {
    check!(r#"start("a") on a new worker"#, { let mut w = Worker::default(); let r = w.start("a".into()); (r, w.current) }, (None, Some("a".to_string())));
}

#[test]
fn start_interrupts() {
    check!(r#"start("a"), start("b")"#, { let mut w = Worker::default(); w.start("a".into()); let r = w.start("b".into()); (r, w.current) }, (Some("a".to_string()), Some("b".to_string())));
}

#[test]
fn finish_moves_to_done() {
    check!(r#"start("a"), finish()"#, { let mut w = Worker::default(); w.start("a".into()); let r = w.finish(); (r, w.current, w.done) }, (true, None, vec!["a".to_string()]));
}

#[test]
fn finish_when_idle() {
    check!(r#"finish() on a new worker"#, { let mut w = Worker::default(); let r = w.finish(); (r, w.current, w.done) }, (false, None, Vec::<String>::new()));
}

#[test]
fn finish_twice() {
    check!(r#"start("a"), finish(), finish()"#, { let mut w = Worker::default(); w.start("a".into()); (w.finish(), w.finish(), w.done) }, (true, false, vec!["a".to_string()]));
}
