use solution::*;

use std::cell::RefCell;

#[test]
fn nested_spans_exit_in_reverse() {
    let log = RefCell::new(Vec::new());
    {
        let _outer = Span::enter("outer", &log);
        let _inner = Span::enter("inner", &log);
    }
    check!("outer, then inner", log.into_inner(), vec!["enter outer", "enter inner", "exit inner", "exit outer"]);
}

fn early(log: &RefCell<Vec<String>>, bail: bool) -> u8 {
    let _s = Span::enter("work", log);
    if bail {
        return 0;
    }
    1
}

#[test]
fn early_return_still_exits() {
    let log = RefCell::new(Vec::new());
    early(&log, true);
    check!("return before the end of the function", log.into_inner(), vec!["enter work", "exit work"]);
}
