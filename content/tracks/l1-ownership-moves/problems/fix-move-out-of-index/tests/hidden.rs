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
fn take_first_no_copy() {
    let mut q = Queue::new("q", vec!["moved".to_string()]);
    let ptr = q.items[0].as_ptr();
    let (s, n) = allocs(|| q.take_first());
    check!(r#"take_first returns the item's own String"#, (s.as_ptr() == ptr, n), (true, 0));
}

#[test]
fn take_first_twice() {
    let mut q = Queue::new("q", vec!["a".to_string()]);
    check!(r#"take_first twice on ["a"]"#, (q.take_first(), q.take_first(), q.items.len()), (String::from("a"), String::new(), 1));
}

#[test]
fn start_next_on_empty() {
    let mut q = Queue::new("q", vec!["only".to_string()]);
    check!(r#"no items: start_next with a current job"#, (q.start_next(), q.start_next(), q.current), (None, Some("only".to_string()), None));
}

#[test]
fn start_next_no_copy() {
    let mut q = Queue::new("q", vec!["b".to_string(), "a".to_string()]);
    q.start_next();
    let ptr = q.current.as_ref().unwrap().as_ptr();
    let (prev, n) = allocs(|| q.start_next());
    check!(r#"the previous job comes back as the same String"#, (prev.map(|s| s.as_ptr() == ptr), n), (Some(true), 0));
}

#[test]
fn finish_without_current() {
    let mut q = Queue::new("q", vec!["a".to_string()]);
    check!(r#"finish on a fresh queue"#, (q.finish(), q.done.len()), (false, 0));
}

#[test]
fn drain_done_no_copy() {
    let mut q = Queue::new("q", vec!["a".to_string(), "b".to_string(), "c".to_string()]);
    for _ in 0..3 {
        q.start_next();
        q.finish();
    }
    let ptr = q.done.as_ptr();
    let (v, n) = allocs(|| q.drain_done());
    check!(r#"drain_done hands over the same Vec"#, (v.as_ptr() == ptr, n, q.done.capacity()), (true, 0, 0));
}

#[test]
fn swap_items_no_copy() {
    let mut a = Queue::new("q", vec!["1".to_string()]);
    let mut b = Queue::new("q", vec!["2".to_string(), "3".to_string()]);
    let (pa, pb) = (a.items.as_ptr(), b.items.as_ptr());
    let (_, n) = allocs(|| a.swap_items(&mut b));
    check!(r#"swap_items moves the buffers"#, (a.items.as_ptr() == pb, b.items.as_ptr() == pa, n), (true, true, 0));
}

#[test]
fn swap_keeps_done() {
    let mut a = Queue::new("q", vec!["x".to_string()]);
    a.start_next();
    a.finish();
    let mut b = Queue::new("q", vec!["y".to_string()]);
    a.swap_items(&mut b);
    check!(r#"swap_items leaves done lists alone"#, (a.done, b.done), (vec!["x".to_string()], Vec::<String>::new()));
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(6113);
    for _ in 0..300 {
        let n = rng.below(5);
        let items: Vec<String> = (0..n).map(|i| format!("j{i}")).collect();
        let mut q = Queue::new("q", items.clone());
        let (mut m_items, mut m_current, mut m_done): (Vec<String>, Option<String>, Vec<String>) = (items, None, Vec::new());
        let mut ops = Vec::new();
        for _ in 0..rng.below(10) {
            match rng.below(4) {
                0 if !m_items.is_empty() => {
                    ops.push("take_first");
                    let want = std::mem::replace(&mut m_items[0], String::new());
                    check!(format!("{ops:?}"), q.take_first(), want);
                }
                1 => {
                    ops.push("start_next");
                    let next = m_items.pop();
                    let want = std::mem::replace(&mut m_current, next);
                    check!(format!("{ops:?}"), q.start_next(), want);
                }
                2 => {
                    ops.push("finish");
                    let want = match m_current.take() {
                        Some(j) => {
                            m_done.push(j);
                            true
                        }
                        None => false,
                    };
                    check!(format!("{ops:?}"), q.finish(), want);
                }
                _ => {
                    ops.push("drain_done");
                    check!(format!("{ops:?}"), q.drain_done(), std::mem::take(&mut m_done));
                }
            }
            check!(format!("{ops:?}, state"), (&q.items, &q.current, &q.done), (&m_items, &m_current, &m_done));
        }
    }
}
