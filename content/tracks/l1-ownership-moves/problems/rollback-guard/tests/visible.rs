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
