use solution::*;

#[test]
fn counts() {
    check!(r#"start = 10"#, { let mut c = counter(10); (c(), c(), c()) }, (11, 12, 13));
}

#[test]
fn independent() {
    check!(r#"two counters from 0"#, { let mut a = counter(0); let mut b = counter(0); a(); a(); b() }, 1);
}
