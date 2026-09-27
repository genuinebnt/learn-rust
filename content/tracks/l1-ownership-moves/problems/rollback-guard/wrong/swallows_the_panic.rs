use std::panic::{AssertUnwindSafe, catch_unwind};

pub fn with_rollback(v: &mut Vec<i32>, f: impl FnOnce(&mut Vec<i32>)) {
    let len = v.len();
    let r = catch_unwind(AssertUnwindSafe(|| f(v)));
    if r.is_err() {
        v.truncate(len);
    }
}
