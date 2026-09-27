use solution::*;

#[test]
fn counts() {
    check!(r#"counter(10), called three times"#, { let mut c = counter(10); (c(), c(), c()) }, (11, 12, 13));
}

#[test]
fn counters_are_independent() {
    check!(r#"two counters from 0: a(), a(), b()"#, { let mut a = counter(0); let mut b = counter(0); a(); a(); b() }, 1);
}

#[test]
fn labeler_outlives_prefix() {
    let f = {
        let p = String::from("id-");
        labeler(&p)
    };
    check!(r#"labeler built from a String that's dropped before the call"#, f(7), "id-7");
}

#[test]
fn above() {
    check!(r#"above_checks([10, 20]) applied to 15"#, above_checks(&[10, 20]).iter().map(|c| c(15)).collect::<Vec<_>>(), vec![true, false]);
}

#[test]
fn greeters_run_later() {
    check!(r#"greeters(["ann", "bo"]), run in order"#, greeters(vec!["ann".into(), "bo".into()]).into_iter().map(|job| job()).collect::<Vec<_>>(), vec!["hello, ann", "hello, bo"]);
}
