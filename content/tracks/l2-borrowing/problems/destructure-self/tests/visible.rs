use solution::*;

#[test]
fn full_cycle() {
    let mut w = Worker { state: State::Idle, log: vec![], max_tries: 3 };
    check!(r#"max 3; start a; retry; finish 7; collect"#, (w.start("a"), w.retry(), w.finish(7), w.collect(), w.state == State::Idle, w.log.clone()), (true, Some(1), true, Some(("a".to_string(), 7)), true, ["start a", "retry a #1", "done a"].map(String::from).to_vec()));
}

#[test]
fn give_up() {
    let mut w = Worker { state: State::Idle, log: vec![], max_tries: 3 };
    w.start("b");
    check!(r#"max 3; start b; retry 3 times"#, (w.retry(), w.retry(), w.retry(), w.state == State::Idle, w.log.last().cloned()), (Some(1), Some(2), None, true, Some("give up b".to_string())));
}

#[test]
fn wrong_state_changes_nothing() {
    let mut w = Worker { state: State::Idle, log: vec![], max_tries: 3 };
    check!(r#"idle: retry, finish, collect"#, (w.retry(), w.finish(1), w.collect(), w.log.len()), (None, false, None, 0));
}

#[test]
fn start_when_busy() {
    let mut w = Worker { state: State::Idle, log: vec![], max_tries: 3 };
    w.start("a");
    check!(r#"start a; start b"#, (w.start("b"), w.state == State::Busy { job: "a".to_string(), tries: 0 }), (false, true));
}

#[test]
fn job_is_moved() {
    let mut w = Worker { state: State::Idle, log: vec![], max_tries: 3 };
    w.start("j");
    let busy = match &w.state { State::Busy { job, .. } => job.as_ptr(), _ => std::ptr::null() };
    w.finish(1);
    let done = match &w.state { State::Done { job, .. } => job.as_ptr(), _ => std::ptr::null() };
    let out = w.collect().unwrap().0.as_ptr();
    check!(r#"start j; finish; collect: the same String throughout"#, (busy == done, done == out), (true, true));
}
