use solution::*;

#[test]
fn current_mut_edits_in_place() {
    check!(r#"start("ab"), uppercase through current_mut()"#, { let mut w = Worker::default(); w.start("ab".into()); if let Some(s) = w.current_mut() { s.make_ascii_uppercase(); } w.current }, Some("AB".to_string()));
}

#[test]
fn current_mut_when_idle() {
    check!(r#"current_mut() on a new worker"#, Worker::default().current_mut().is_none(), true);
}

#[test]
fn current_mut_then_finish() {
    check!(r#"start("a"), uppercase through current_mut(), finish()"#, { let mut w = Worker::default(); w.start("a".into()); if let Some(s) = w.current_mut() { s.make_ascii_uppercase(); } w.finish(); (w.current, w.done) }, (None, vec!["A".to_string()]));
}

#[test]
fn interrupted_task_is_not_done() {
    check!(r#"start("a"), start("b"), finish()"#, { let mut w = Worker::default(); w.start("a".into()); w.start("b".into()); w.finish(); (w.current, w.done) }, (None, vec!["b".to_string()]));
}

#[test]
fn empty_task_name() {
    check!(r#"start(""), finish(), finish()"#, { let mut w = Worker::default(); w.start(String::new()); (w.finish(), w.finish(), w.current, w.done) }, (true, false, None, vec![String::new()]));
}

#[test]
fn restart_after_finish() {
    check!(r#"start("a"), finish(), start("b")"#, { let mut w = Worker::default(); w.start("a".into()); w.finish(); let r = w.start("b".into()); (r, w.current, w.done) }, (None, Some("b".to_string()), vec!["a".to_string()]));
}

#[test]
fn done_keeps_order() {
    check!(r#"a, b, c each started and finished"#, { let mut w = Worker::default(); for t in ["a", "b", "c"] { w.start(t.into()); w.finish(); } w.done }, vec!["a".to_string(), "b".to_string(), "c".to_string()]);
}

#[test]
fn same_task_twice() {
    check!(r#"start("a"), start("a")"#, { let mut w = Worker::default(); w.start("a".into()); let r = w.start("a".into()); (r, w.current) }, (Some("a".to_string()), Some("a".to_string())));
}

#[test]
fn unicode_task() {
    check!(r#"start("修复 🦀"), finish()"#, { let mut w = Worker::default(); w.start("修复 🦀".into()); (w.finish(), w.done) }, (true, vec!["修复 🦀".to_string()]));
}

#[test]
fn start_keeps_done() {
    check!(r#"done = ["x"], start("a")"#, { let mut w = Worker { current: None, done: vec!["x".into()] }; w.start("a".into()); w.done }, vec!["x".to_string()]);
}

#[test]
fn start_moves_not_copies() {
    let t = String::from("a");
    let p = t.as_ptr();
    check!(r#"start(t) returns the same buffer later"#, { let mut w = Worker::default(); w.start(t); w.start("b".into()).map(|s| s.as_ptr()) }, Some(p));
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(1314);
    let names = ["a", "b", "", "ç"];
    for _ in 0..300 {
        let mut w = Worker::default();
        let mut cur: Option<String> = None;
        let mut done: Vec<String> = Vec::new();
        let mut log: Vec<String> = Vec::new();
        let n = rng.below(8);
        for _ in 0..n {
            if rng.bool() {
                let t = rng.pick(&names).to_string();
                log.push(format!("start({t:?})"));
                let want = std::mem::replace(&mut cur, Some(t.clone()));
                check!(log.join(", "), w.start(t), want);
            } else {
                log.push("finish()".to_string());
                let want = match std::mem::take(&mut cur) {
                    Some(t) => {
                        done.push(t);
                        true
                    }
                    None => false,
                };
                check!(log.join(", "), w.finish(), want);
            }
        }
        check!(format!("state after {}", log.join(", ")), (w.current, w.done), (cur, done));
    }
}

#[test]
fn many_tasks() {
    let mut w = Worker::default();
    for i in 0..100_000 {
        w.start(i.to_string());
        w.finish();
    }
    check!("100000 tasks started and finished", (w.current, w.done.len(), w.done[99_999].clone()), (None, 100_000, "99999".to_string()));
}
