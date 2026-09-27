use solution::*;

#[test]
fn counts() {
    check!(r#"start = 10"#, { let mut c = counter(10); (c(), c(), c()) }, (11, 12, 13));
}

#[test]
fn independent() {
    check!(r#"two counters from 0"#, { let mut a = counter(0); let mut b = counter(0); a(); a(); b() }, 1);
}

#[test]
fn first_call() {
    check!(r#"start = 0, one call"#, { let mut c = counter(0); c() }, 1);
}

#[test]
fn five_calls() {
    check!(r#"start = 1, five calls"#, { let mut c = counter(1); (0..5).map(|_| c()).collect::<Vec<_>>() }, vec![2, 3, 4, 5, 6]);
}

#[test]
fn start_not_returned() {
    check!(r#"start = 42"#, { let mut c = counter(42); c() }, 43);
}
