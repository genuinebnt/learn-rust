use solution::*;

#[test]
fn hundred_calls() {
    check!(r#"start = 0, 100 calls"#, { let mut c = counter(0); (0..100).map(|_| c()).last() }, Some(100));
}

#[test]
fn near_max() {
    check!(r#"start = u32::MAX - 2, two calls"#, { let mut c = counter(u32::MAX - 2); (c(), c()) }, (u32::MAX - 1, u32::MAX));
}

#[test]
fn interleaved() {
    check!(r#"a and b from 5, called a, b, a, b"#, { let mut a = counter(5); let mut b = counter(5); (a(), b(), a(), b()) }, (6, 6, 7, 7));
}

#[test]
fn different_starts() {
    check!(r#"counter(0) and counter(100)"#, { let mut a = counter(0); let mut b = counter(100); (a(), b(), a()) }, (1, 101, 2));
}

#[test]
fn boxed() {
    check!(r#"Box<dyn FnMut() -> u32> from counter(3)"#, { let mut c: Box<dyn FnMut() -> u32> = Box::new(counter(3)); (c(), c()) }, (4, 5));
}

#[test]
fn start_variable_dropped() {
    check!(r#"start comes from a local that goes away"#, { let mut c = { let s = String::from("41"); counter(s.parse().unwrap()) }; c() }, 42);
}

#[test]
fn many_calls() {
    check!(r#"start = 0, 100000 calls"#, { let mut c = counter(0); let mut last = 0; for _ in 0..100_000 { last = c(); } last }, 100_000);
}

fn call_twice(mut f: impl FnMut() -> u32) -> (u32, u32) {
    (f(), f())
}

#[test]
fn passed_by_value() {
    check!("call_twice(counter(7))", call_twice(counter(7)), (8, 9));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1111);
    for _ in 0..300 {
        let start = rng.int(0, 1_000_000) as u32;
        let calls = rng.below(20) + 1;
        let mut c = counter(start);
        let got: Vec<u32> = (0..calls).map(|_| c()).collect();
        let want: Vec<u32> = (1..=calls as u32).map(|k| start + k).collect();
        check!(format!("start = {start}, {calls} calls"), got, want);
    }
}
