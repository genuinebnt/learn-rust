use solution::*;

#[test]
fn submit_once() {
    let s = Scheduler::new();
    check!(r#"submit 3, 3, 5"#, (s.submit(3), s.submit(3), s.submit(5), s.count(3)), (true, false, true, 2));
}

#[test]
fn count_unknown() {
    let s = Scheduler::new();
    check!(r#"count(9) on a new scheduler"#, (s.count(9), s.known()), (0, 1));
}

#[test]
fn run_follow_ups() {
    let s = Scheduler::new();
    s.submit(12);
    check!(r#"submit 12; run"#, (s.run(), s.done()), (3, vec![12, 6, 3]));
}

#[test]
fn run_newest_first() {
    let s = Scheduler::new();
    for j in [1, 5, 7] {
        s.submit(j);
    }
    check!(r#"submit 1, 5, 7; run"#, (s.run(), s.done()), (3, vec![7, 5, 1]));
}

#[test]
fn follow_up_already_seen() {
    let s = Scheduler::new();
    s.submit(3);
    s.submit(6);
    check!(r#"submit 3, 6; run"#, (s.run(), s.done(), s.count(3)), (2, vec![6, 3], 2));
}
