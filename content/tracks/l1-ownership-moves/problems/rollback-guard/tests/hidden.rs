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
