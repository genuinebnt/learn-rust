use solution::*;

#[test]
fn none_bad() {
    check!(r#"n = 10, none bad"#, first_bad(10, |_| false), None);
}

#[test]
fn first_is_bad_at_max_n() {
    let calls = std::cell::Cell::new(0);
    let found = first_bad(u32::MAX, |v| {
        calls.set(calls.get() + 1);
        v >= 1
    });
    check!(r#"n = u32::MAX, every version bad"#, (found, calls.get() <= 33), (Some(1), true));
}

#[test]
fn only_max_is_bad() {
    check!(r#"n = u32::MAX, first bad u32::MAX"#, first_bad(u32::MAX, |v| v == u32::MAX), Some(u32::MAX));
}

#[test]
fn two_versions() {
    check!(r#"n = 2, first bad 2, and first bad 1"#, (first_bad(2, |v| v >= 2), first_bad(2, |v| v >= 1)), (Some(2), Some(1)));
}

#[test]
fn never_asks_about_version_zero() {
    check!(r#"n = 7, first bad 3; is_bad panics on 0 or > n"#, first_bad(7, |v| { assert!((1..=7).contains(&v)); v >= 3 }), Some(3));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(403);
    for _ in 0..400 {
        let n = rng.int(0, 2000) as u32;
        let bad_from = rng.int(1, i64::from(n) + 1) as u32;
        let calls = std::cell::Cell::new(0u32);
        let got = first_bad(n, |v| {
            calls.set(calls.get() + 1);
            v >= bad_from
        });
        let want = (1..=n).find(|&v| v >= bad_from);
        check!(format!("n = {n}, first bad = {bad_from} (at most 13 calls)"), (got, calls.get() <= 13), (want, true));
    }
}

#[test]
fn max_n() {
    check!(r#"n = u32::MAX, first bad u32::MAX - 1"#, first_bad(u32::MAX, |v| v >= u32::MAX - 1), Some(u32::MAX - 1));
}

#[test]
fn few_calls() {
    let calls = std::cell::Cell::new(0);
    let found = first_bad(u32::MAX, |v| {
        calls.set(calls.get() + 1);
        v >= 123_456_789
    });
    check!(r#"n = u32::MAX, count calls"#, (found, calls.get() <= 33), (Some(123_456_789), true));
}
