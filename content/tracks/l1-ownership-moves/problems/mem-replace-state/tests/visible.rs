use solution::*;

#[test]
fn queued_to_running() {
    check!(r#"Queued("build")"#, { let mut j = Job::Queued("build".into()); advance(&mut j); j }, Job::Running("build".into()));
}

#[test]
fn running_to_done() {
    check!(r#"Running("build")"#, { let mut j = Job::Running("build".into()); advance(&mut j); j }, Job::Done("build".into()));
}

#[test]
fn done_stays_done() {
    check!(r#"Done("ship")"#, { let mut j = Job::Done("ship".into()); advance(&mut j); j }, Job::Done("ship".into()));
}

#[test]
fn two_steps() {
    check!(r#"Queued("test") advanced twice"#, { let mut j = Job::Queued("test".into()); advance(&mut j); advance(&mut j); j }, Job::Done("test".into()));
}

#[test]
fn three_steps() {
    check!(r#"Queued("lint") advanced three times"#, { let mut j = Job::Queued("lint".into()); for _ in 0..3 { advance(&mut j); } j }, Job::Done("lint".into()));
}
