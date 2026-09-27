use solution::*;

use std::panic::{AssertUnwindSafe, catch_unwind};

#[test]
fn panic_rolls_back() {
    let mut v = vec![1];
    let r = catch_unwind(AssertUnwindSafe(|| {
        with_rollback(&mut v, |v| {
            v.push(2);
            v.push(3);
            panic!("boom");
        })
    }));
    check!("f pushes 2 and 3, then panics", (r.is_err(), v), (true, vec![1]));
}

#[test]
fn success_keeps_pushes() {
    let mut v = vec![1];
    with_rollback(&mut v, |v| v.push(2));
    check!("f pushes 2 and returns", v, vec![1, 2]);
}

#[test]
fn panic_without_pushes() {
    let mut v = vec![1, 2];
    let r = catch_unwind(AssertUnwindSafe(|| with_rollback(&mut v, |_| panic!("boom"))));
    check!("f panics at once", (r.is_err(), v), (true, vec![1, 2]));
}

#[test]
fn success_on_empty() {
    let mut v = vec![];
    with_rollback(&mut v, |v| {
        v.push(1);
        v.push(2);
    });
    check!("v = [], f pushes 1 and 2", v, vec![1, 2]);
}

#[test]
fn rollback_keeps_earlier_values() {
    let mut v = vec![7, 8, 9];
    let _ = catch_unwind(AssertUnwindSafe(|| {
        with_rollback(&mut v, |v| {
            v.push(10);
            panic!("boom");
        })
    }));
    check!("v = [7, 8, 9], f pushes 10 then panics", v, vec![7, 8, 9]);
}
