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

#[test]
fn panic_in_nested_spans() {
    let log = RefCell::new(Vec::new());
    let _ = catch_unwind(AssertUnwindSafe(|| {
        let _outer = Span::enter("outer", &log);
        let _inner = Span::enter("inner", &log);
        panic!("boom");
    }));
    check!("a panic inside two spans", log.into_inner(), vec!["enter outer", "enter inner", "exit inner", "exit outer"]);
}

#[test]
fn nothing_before_the_drop() {
    let log = RefCell::new(Vec::new());
    let s = Span::enter("held", &log);
    let before = log.borrow().clone();
    drop(s);
    check!("the log while the span is alive", before, vec!["enter held"]);
}

#[test]
fn explicit_drop_exits_early() {
    let log = RefCell::new(Vec::new());
    {
        let a = Span::enter("a", &log);
        drop(a);
        let _b = Span::enter("b", &log);
    }
    check!("drop(a), then enter b", log.into_inner(), vec!["enter a", "exit a", "enter b", "exit b"]);
}

fn take(_s: Span<'_>) {}

#[test]
fn moved_span_exits_where_it_ends() {
    let log = RefCell::new(Vec::new());
    {
        let s = Span::enter("moved", &log);
        take(s);
        let _after = Span::enter("after", &log);
    }
    check!("span moved into a function that drops it", log.into_inner(), vec!["enter moved", "exit moved", "enter after", "exit after"]);
}

#[test]
fn in_a_loop() {
    let log = RefCell::new(Vec::new());
    for name in ["x", "y"] {
        let _s = Span::enter(name, &log);
    }
    check!("a span per loop iteration", log.into_inner(), vec!["enter x", "exit x", "enter y", "exit y"]);
}

#[test]
fn forgotten_span_never_exits() {
    let log = RefCell::new(Vec::new());
    std::mem::forget(Span::enter("lost", &log));
    check!("mem::forget(span)", log.into_inner(), vec!["enter lost"]);
}

#[test]
fn random_vs_model() {
    const NAMES: [&str; 4] = ["p", "q", "r", "s"];
    let mut rng = anneal_prelude::Rng::new(1110);
    for _ in 0..200 {
        let log = RefCell::new(Vec::new());
        let mut want = Vec::new();
        let mut ops = Vec::new();
        {
            let mut open: Vec<(Span, &str)> = Vec::new();
            for _ in 0..rng.below(12) {
                if rng.bool() || open.is_empty() {
                    let name = *rng.pick(&NAMES);
                    want.push(format!("enter {name}"));
                    ops.push(format!("enter {name}"));
                    open.push((Span::enter(name, &log), name));
                } else {
                    let i = rng.below(open.len());
                    let (span, name) = open.remove(i);
                    want.push(format!("exit {name}"));
                    ops.push(format!("drop {name}"));
                    drop(span);
                }
            }
            while let Some((span, name)) = open.pop() {
                want.push(format!("exit {name}"));
                drop(span);
            }
        }
        check!(format!("{ops:?}, then the rest in reverse"), log.into_inner(), want);
    }
}
