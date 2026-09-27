use solution::*;

#[test]
fn done_stays() {
    check!(r#"Done("x")"#, { let mut j = Job::Done("x".into()); advance(&mut j); j }, Job::Done("x".into()));
}

#[test]
fn same_buffer() {
    check!(r#"name's heap buffer kept"#, { let mut j = Job::Queued(String::from("keep")); let p = match &j { Job::Queued(s) => s.as_ptr(), _ => unreachable!() }; advance(&mut j); match &j { Job::Running(s) => s.as_ptr() == p, _ => false } }, true);
}
