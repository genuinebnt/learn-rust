use solution::*;

use std::panic::{AssertUnwindSafe, catch_unwind};

#[test]
fn nested_rollbacks() {
    let mut v = vec![];
    with_rollback(&mut v, |v| {
        v.push(1);
        let _ = catch_unwind(AssertUnwindSafe(|| with_rollback(v, |v| {
            v.push(2);
            panic!("inner");
        })));
        v.push(3);
    });
    check!("outer keeps 1 and 3; inner rolls back 2", v, vec![1, 3]);
}

#[test]
fn panic_keeps_propagating() {
    let mut v = vec![1];
    let r = catch_unwind(AssertUnwindSafe(|| with_rollback(&mut v, |_| panic!("boom"))));
    let msg = r.err().and_then(|e| e.downcast_ref::<&str>().map(|s| s.to_string()));
    check!("f panics with \"boom\"", msg, Some("boom".to_string()));
}

#[test]
fn outer_panic_undoes_inner_success() {
    let mut v = vec![0];
    let _ = catch_unwind(AssertUnwindSafe(|| {
        with_rollback(&mut v, |v| {
            with_rollback(v, |v| v.push(1));
            v.push(2);
            panic!("outer");
        })
    }));
    check!("inner succeeds, outer panics", v, vec![0]);
}

#[test]
fn empty_and_panic() {
    let mut v = vec![];
    let _ = catch_unwind(AssertUnwindSafe(|| with_rollback(&mut v, |v| {
        v.push(9);
        panic!("boom");
    })));
    check!("v = [], f pushes 9 then panics", v, Vec::<i32>::new());
}

#[test]
fn success_without_pushes() {
    let mut v = vec![4, 5];
    with_rollback(&mut v, |_| {});
    check!("v = [4, 5], f does nothing", v, vec![4, 5]);
}

#[test]
fn success_then_panic() {
    let mut v = vec![];
    with_rollback(&mut v, |v| v.push(1));
    let _ = catch_unwind(AssertUnwindSafe(|| with_rollback(&mut v, |v| {
        v.push(2);
        panic!("boom");
    })));
    with_rollback(&mut v, |v| v.push(3));
    check!("push 1 ok, push 2 panics, push 3 ok", v, vec![1, 3]);
}

#[test]
fn big_rollback() {
    let mut v: Vec<i32> = (0..1000).collect();
    let _ = catch_unwind(AssertUnwindSafe(|| with_rollback(&mut v, |v| {
        v.extend(0..200_000);
        panic!("boom");
    })));
    check!("v = 0..1000, f pushes 200000 then panics", (v.len(), v[999]), (1000, 999));
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(1117);
    for _ in 0..60 {
        let len = rng.below(5);
        let mut v: Vec<i32> = rng.vec(len, -9, 9);
        let adds = rng.below(5);
        let pushes: Vec<i32> = rng.vec(adds, -9, 9);
        let fails = rng.bool();
        let mut want = v.clone();
        if !fails {
            want.extend(&pushes);
        }
        let input = format!("v = {v:?}, f pushes {pushes:?}, panics: {fails}");
        let _ = catch_unwind(AssertUnwindSafe(|| with_rollback(&mut v, |v| {
            v.extend(&pushes);
            if fails {
                panic!("random");
            }
        })));
        check!(input, v, want);
    }
}
