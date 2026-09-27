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

#[test]
fn finish_records_status_once() {
    let log = RefCell::new(Vec::new());
    {
        let s = Span::enter("job", &log);
        s.finish("ok");
    }
    check!("enter job, finish(\"ok\")", log.into_inner(), vec!["enter job", "exit job: ok"]);
}

#[test]
fn finish_inner_then_outer_drops() {
    let log = RefCell::new(Vec::new());
    {
        let _outer = Span::enter("outer", &log);
        let inner = Span::enter("inner", &log);
        inner.finish("done");
    }
    check!("inner finished, outer dropped", log.into_inner(), vec!["enter outer", "enter inner", "exit inner: done", "exit outer"]);
}

#[test]
fn let_underscore_exits_at_once() {
    let log = RefCell::new(Vec::new());
    {
        let _ = Span::enter("gone", &log);
        let _kept = Span::enter("kept", &log);
    }
    check!("let _ = Span::enter(..), then let _kept", log.into_inner(), vec!["enter gone", "exit gone", "enter kept", "exit kept"]);
}
