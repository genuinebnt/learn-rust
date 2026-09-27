use solution::*;

#[test]
fn max_one() {
    let mut w = Worker { state: State::Idle, log: vec![], max_tries: 1 };
    w.start("x");
    check!(r#"max 1; start; retry"#, (w.retry(), w.log.clone()), (None, ["start x", "give up x"].map(String::from).to_vec()));
}

#[test]
fn finish_when_done() {
    let mut w = Worker { state: State::Idle, log: vec![], max_tries: 3 };
    w.start("x");
    w.finish(1);
    check!(r#"start; finish 1; finish 2"#, (w.finish(2), w.collect()), (false, Some(("x".to_string(), 1))));
}

#[test]
fn start_when_done() {
    let mut w = Worker { state: State::Idle, log: vec![], max_tries: 3 };
    w.start("x");
    w.finish(1);
    check!(r#"start; finish; start y"#, (w.start("y"), w.log.len()), (false, 2));
}

#[test]
fn collect_twice() {
    let mut w = Worker { state: State::Idle, log: vec![], max_tries: 3 };
    w.start("x");
    w.finish(1);
    check!(r#"start; finish; collect twice"#, (w.collect().is_some(), w.collect()), (true, None));
}

#[test]
fn restart_after_give_up() {
    let mut w = Worker { state: State::Idle, log: vec![], max_tries: 3 };
    w.start("a");
    for _ in 0..3 {
        w.retry();
    }
    check!(r#"max 3; start a; retry x3; start b; retry"#, (w.start("b"), w.retry(), w.log.len()), (true, Some(1), 6));
}

#[test]
fn retry_after_finish() {
    let mut w = Worker { state: State::Idle, log: vec![], max_tries: 3 };
    w.start("x");
    w.finish(5);
    check!(r#"start; finish; retry"#, (w.retry(), w.state == State::Done { job: "x".to_string(), result: 5 }), (None, true));
}

#[test]
fn unicode_job() {
    let mut w = Worker { state: State::Idle, log: vec![], max_tries: 3 };
    w.start("日本");
    w.finish(0);
    check!(r#"start 日本; finish 0; collect"#, (w.collect(), w.log.clone()), (Some(("日本".to_string(), 0)), ["start 日本", "done 日本"].map(String::from).to_vec()));
}

#[test]
fn tries_kept_in_state() {
    let mut w = Worker { state: State::Idle, log: vec![], max_tries: 5 };
    w.start("t");
    w.retry();
    w.retry();
    check!(r#"max 5; start; retry x2"#, w.state, State::Busy { job: "t".to_string(), tries: 2 });
}

#[test]
fn random_vs_model() {
    // 0 idle, 1 busy, 2 done
    let mut rng = anneal_prelude::Rng::new(6226);
    for _ in 0..300 {
        let max = 1 + rng.below(3) as u32;
        let mut w = Worker { state: State::Idle, log: vec![], max_tries: max };
        let (mut phase, mut job, mut tries, mut result) = (0, String::new(), 0u32, 0u64);
        let mut log: Vec<String> = Vec::new();
        let mut ops = Vec::new();
        for step in 0..8 {
            match rng.below(4) {
                0 => {
                    let name = format!("j{step}");
                    let want = phase == 0;
                    if want {
                        phase = 1;
                        job = name.clone();
                        tries = 0;
                        log.push(format!("start {name}"));
                    }
                    ops.push(format!("start {name}"));
                    check!(format!("max {max}; {}", ops.join(", ")), w.start(&name), want);
                }
                1 => {
                    let want = if phase == 1 {
                        tries += 1;
                        if tries < max {
                            log.push(format!("retry {job} #{tries}"));
                            Some(tries)
                        } else {
                            log.push(format!("give up {job}"));
                            phase = 0;
                            None
                        }
                    } else {
                        None
                    };
                    ops.push("retry".to_string());
                    check!(format!("max {max}; {}", ops.join(", ")), w.retry(), want);
                }
                2 => {
                    let want = phase == 1;
                    if want {
                        phase = 2;
                        result = step as u64;
                        log.push(format!("done {job}"));
                    }
                    ops.push(format!("finish {step}"));
                    check!(format!("max {max}; {}", ops.join(", ")), w.finish(step as u64), want);
                }
                _ => {
                    let want = if phase == 2 {
                        phase = 0;
                        Some((job.clone(), result))
                    } else {
                        None
                    };
                    ops.push("collect".to_string());
                    check!(format!("max {max}; {}", ops.join(", ")), w.collect(), want);
                }
            }
        }
        check!(format!("max {max}; {}; log", ops.join(", ")), w.log.clone(), log);
    }
}
