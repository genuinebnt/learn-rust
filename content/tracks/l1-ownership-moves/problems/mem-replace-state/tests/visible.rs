use solution::*;

#[test]
fn queued_to_running() {
    check!(r#"Queued("build")"#, { let mut j = Job::Queued("build".into()); advance(&mut j); j }, Job::Running("build".into()));
}

#[test]
fn running_to_done() {
    check!(r#"Running("build")"#, { let mut j = Job::Running("build".into()); advance(&mut j); j }, Job::Done("build".into()));
}
