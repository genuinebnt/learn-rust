use solution::*;

#[test]
fn done_stays() {
    check!(r#"Done("x")"#, { let mut j = Job::Done("x".into()); advance(&mut j); j }, Job::Done("x".into()));
}

#[test]
fn same_buffer() {
    check!(r#"name's heap buffer kept"#, { let mut j = Job::Queued(String::from("keep")); let p = match &j { Job::Queued(s) => s.as_ptr(), _ => unreachable!() }; advance(&mut j); match &j { Job::Running(s) => s.as_ptr() == p, _ => false } }, true);
}

#[test]
fn same_buffer_to_done() {
    check!(r#"Running → Done keeps the buffer"#, { let mut j = Job::Running(String::from("keep")); let p = match &j { Job::Running(s) => s.as_ptr(), _ => unreachable!() }; advance(&mut j); match &j { Job::Done(s) => s.as_ptr() == p, _ => false } }, true);
}

#[test]
fn done_keeps_buffer() {
    check!(r#"Done stays Done with the same buffer"#, { let mut j = Job::Done(String::from("keep")); let p = match &j { Job::Done(s) => s.as_ptr(), _ => unreachable!() }; advance(&mut j); match &j { Job::Done(s) => s.as_ptr() == p, _ => false } }, true);
}

#[test]
fn done_twice() {
    check!(r#"Done("x") advanced twice"#, { let mut j = Job::Done("x".into()); advance(&mut j); advance(&mut j); j }, Job::Done("x".into()));
}

#[test]
fn ten_steps() {
    check!(r#"Queued("q") advanced 10 times"#, { let mut j = Job::Queued("q".into()); for _ in 0..10 { advance(&mut j); } j }, Job::Done("q".into()));
}

#[test]
fn empty_name() {
    check!(r#"Queued("")"#, { let mut j = Job::Queued(String::new()); advance(&mut j); j }, Job::Running(String::new()));
}

#[test]
fn unicode_name() {
    check!(r#"Running("日本 ✓")"#, { let mut j = Job::Running("日本 ✓".into()); advance(&mut j); j }, Job::Done("日本 ✓".into()));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1115);
    for _ in 0..300 {
        let len = rng.below(5);
        let name = rng.string(len, "ab");
        let start = rng.below(3);
        let steps = rng.below(4);
        let make = |stage: usize, name: String| match stage {
            0 => Job::Queued(name),
            1 => Job::Running(name),
            _ => Job::Done(name),
        };
        let mut job = make(start, name.clone());
        let input = format!("{job:?}, advanced {steps} times");
        for _ in 0..steps {
            advance(&mut job);
        }
        check!(input, job, make((start + steps).min(2), name));
    }
}
