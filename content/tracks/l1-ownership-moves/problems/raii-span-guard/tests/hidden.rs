use solution::*;

use std::cell::RefCell;
use std::panic::{AssertUnwindSafe, catch_unwind};

#[test]
fn panic_still_exits() {
    let log = RefCell::new(Vec::new());
    let _ = catch_unwind(AssertUnwindSafe(|| {
        let _s = Span::enter("risky", &log);
        panic!("boom");
    }));
    check!("a panic inside the span", log.into_inner(), vec!["enter risky", "exit risky"]);
}
