use solution::*;

use std::alloc::{GlobalAlloc, Layout, System};
use std::cell::Cell;

struct CountingAlloc;

thread_local! {
    static ALLOCS: Cell<usize> = const { Cell::new(0) };
}

unsafe impl GlobalAlloc for CountingAlloc {
    unsafe fn alloc(&self, layout: Layout) -> *mut u8 {
        let _ = ALLOCS.try_with(|n| n.set(n.get() + 1));
        unsafe { System.alloc(layout) }
    }

    unsafe fn dealloc(&self, ptr: *mut u8, layout: Layout) {
        unsafe { System.dealloc(ptr, layout) }
    }
}

#[global_allocator]
static GLOBAL: CountingAlloc = CountingAlloc;

/// Runs `f` and returns its result with the number of allocations it made.
fn allocs<R>(f: impl FnOnce() -> R) -> (R, usize) {
    let before = ALLOCS.with(|n| n.get());
    let r = f();
    (r, ALLOCS.with(|n| n.get()) - before)
}

#[test]
fn push_allocates_one_node() {
    let mut s = Stack::new();
    for i in 1..=3 {
        s.push(i);
    }
    check!(r#"push onto a stack of 3"#, { let (_, n) = allocs(|| s.push(4)); n }, 1);
}

#[test]
fn reverse_allocates_nothing() {
    let mut s = Stack::new();
    for i in 0..100 {
        s.push(i);
    }
    check!(r#"reverse a stack of 100"#, { let (_, n) = allocs(|| s.reverse()); (n, s.peek().copied(), s.len()) }, (0, Some(0), 100));
}

#[test]
fn move_top_allocates_nothing() {
    let mut a = Stack::new();
    for i in 0..10 {
        a.push(i);
    }
    let mut b = Stack::new();
    check!(r#"move_top_to 5 times"#, { let (_, n) = allocs(|| for _ in 0..5 { a.move_top_to(&mut b); }); (n, a.len(), b.len()) }, (0, 5, 5));
}

#[test]
fn value_stays_in_its_box() {
    let mut s = Stack::new();
    for w in ["a", "b", "c"] {
        s.push(w.to_string());
    }
    check!(r#"the top value's address before and after two reverses"#, { let before = s.peek().map(|v| v as *const String); s.reverse(); s.reverse(); s.peek().map(|v| v as *const String) == before }, true);
}

#[test]
fn reverse_empty_and_single() {
    let mut e: Stack<i32> = Stack::new();
    let mut o = Stack::new();
    o.push(7);
    check!(r#"reverse [] and [7]"#, { e.reverse(); o.reverse(); (e.len(), o.into_vec()) }, (0, vec![7]));
}

#[test]
fn len_after_moves() {
    let mut a = Stack::new();
    for i in 1..=3 {
        a.push(i);
    }
    let mut b = Stack::new();
    check!(r#"a = [1, 2, 3], move two to b, pop from b"#, { a.move_top_to(&mut b); a.move_top_to(&mut b); (b.pop(), a.len(), b.len()) }, (Some(2), 1, 1));
}

#[test]
fn drops_every_value() {
    let rc = std::rc::Rc::new(());
    let mut s = Stack::new();
    for _ in 0..3 {
        s.push(rc.clone());
    }
    check!(r#"Rc values: drop a stack of 3 clones"#, { drop(s); std::rc::Rc::strong_count(&rc) }, 1);
}

#[test]
fn peek_after_pop() {
    let mut s = Stack::new();
    s.push("a".to_string());
    s.push("b".to_string());
    check!(r#"push a, b; pop; peek"#, { s.pop(); s.peek().cloned() }, Some("a".to_string()));
}

#[test]
fn drop_a_million_nodes() {
    // Runs on its own thread with a small stack, so a recursive drop overflows.
    let t = std::thread::Builder::new().stack_size(256 * 1024).spawn(|| {
        let mut s = Stack::new();
        for i in 0..1_000_000u64 {
            s.push(i);
        }
        let top = s.peek().copied();
        drop(s);
        top
    });
    check!("drop a stack of 1000000 nodes", t.unwrap().join().ok(), Some(Some(999_999)));
}

#[test]
fn into_vec_a_million_nodes() {
    let mut s = Stack::new();
    for i in 0..1_000_000u64 {
        s.push(i);
    }
    s.reverse();
    let v = s.into_vec();
    check!("1000000 nodes, reversed, into_vec", (v.len(), v[0], v[999_999]), (1_000_000, 0, 999_999));
}

#[test]
fn random_vs_vec_model() {
    let mut rng = anneal_prelude::Rng::new(6114);
    for _ in 0..300 {
        let (mut a, mut b) = (Stack::new(), Stack::new());
        let (mut ma, mut mb): (Vec<i32>, Vec<i32>) = (Vec::new(), Vec::new());
        let mut ops = Vec::new();
        for _ in 0..rng.below(16) {
            match rng.below(5) {
                0 | 1 => {
                    let v = rng.int(0, 9) as i32;
                    ops.push(format!("a.push({v})"));
                    a.push(v);
                    ma.push(v);
                }
                2 => {
                    ops.push("a.pop()".to_string());
                    check!(format!("{ops:?}"), a.pop(), ma.pop());
                }
                3 => {
                    ops.push("a.reverse()".to_string());
                    a.reverse();
                    ma.reverse();
                }
                _ => {
                    ops.push("a.move_top_to(b)".to_string());
                    let want = match ma.pop() {
                        Some(v) => {
                            mb.push(v);
                            true
                        }
                        None => false,
                    };
                    check!(format!("{ops:?}"), a.move_top_to(&mut b), want);
                }
            }
            check!(format!("{ops:?}: len, peek"), (a.len(), a.peek(), b.len(), b.peek()), (ma.len(), ma.last(), mb.len(), mb.last()));
        }
        let (va, vb): (Vec<i32>, Vec<i32>) = (ma.iter().rev().copied().collect(), mb.iter().rev().copied().collect());
        check!(format!("{ops:?}: into_vec"), (a.into_vec(), b.into_vec()), (va, vb));
    }
}
