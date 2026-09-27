use solution::*;

#[test]
fn near_max() {
    check!(r#"counter(u32::MAX - 2), two calls"#, { let mut c = counter(u32::MAX - 2); (c(), c()) }, (u32::MAX - 1, u32::MAX));
}

#[test]
fn boxed_counter() {
    check!(r#"counter(3) as Box<dyn FnMut() -> u32>"#, { let mut c: Box<dyn FnMut() -> u32> = Box::new(counter(3)); (c(), c()) }, (4, 5));
}

#[test]
fn labeler_empty_prefix() {
    check!(r#"labeler("")(0)"#, labeler("")(0), "0");
}

#[test]
fn labeler_called_twice() {
    check!(r##"labeler("#") on 1 and 22"##, { let f = labeler("#"); (f(1), f(22)) }, ("#1".to_string(), "#22".to_string()));
}

#[test]
fn labeler_prefix_changed_later() {
    check!(r#"prefix String changed after labeler"#, { let mut p = String::from("a-"); let f = labeler(&p); p.push_str("zzz"); (f(1), p) }, ("a-1".to_string(), "a-zzz".to_string()));
}

#[test]
fn above_is_strict() {
    check!(r#"above_checks([5]) applied to 5 and 6"#, { let c = above_checks(&[5]); (c[0](5), c[0](6)) }, (false, true));
}

#[test]
fn above_empty() {
    check!(r#"above_checks([])"#, above_checks(&[]).len(), 0);
}

#[test]
fn above_outlives_limits() {
    check!(r#"checks kept after the limits Vec is dropped"#, { let checks = { let limits = vec![0, u32::MAX - 1]; above_checks(&limits) }; (checks[0](1), checks[1](u32::MAX)) }, (true, true));
}

#[test]
fn greeters_unicode_and_empty() {
    check!(r#"greeters(["", "zoë"])"#, greeters(vec![String::new(), "zoë".into()]).into_iter().map(|job| job()).collect::<Vec<_>>(), vec!["hello, ", "hello, zoë"]);
}

#[test]
fn greeters_out_of_order() {
    check!(r#"run the second job first"#, { let mut jobs = greeters(vec!["a".into(), "b".into()]); let second = jobs.pop().unwrap(); let first = jobs.pop().unwrap(); (second(), first()) }, ("hello, b".to_string(), "hello, a".to_string()));
}

#[test]
fn greeters_keep_the_names() {
    // Each job owns its name: the Strings move into the closures, they aren't copied.
    let names: Vec<String> = vec!["left".into(), "right".into()];
    let lens: Vec<usize> = names.iter().map(|n| n.len()).collect();
    let jobs = greeters(names);
    check!("greeters([\"left\", \"right\"]).len()", (jobs.len(), lens), (2, vec![4, 5]));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(6110);
    for _ in 0..200 {
        let start = rng.int(0, 1_000_000) as u32;
        let calls = rng.below(20) + 1;
        let mut c = counter(start);
        let got: Vec<u32> = (0..calls).map(|_| c()).collect();
        let want: Vec<u32> = (1..=calls as u32).map(|k| start + k).collect();
        check!(format!("counter({start}), {calls} calls"), got, want);
        let k = rng.below(5);
        let limits: Vec<u32> = rng.vec(k, 0, 20);
        let x = rng.below(21) as u32;
        let got: Vec<bool> = above_checks(&limits).iter().map(|f| f(x)).collect();
        check!(format!("above_checks({limits:?}) applied to {x}"), got, limits.iter().map(|&l| x > l).collect::<Vec<_>>());
    }
}
