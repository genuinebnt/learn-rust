---
title: Box, Rc and Arc: owning things on the heap, alone or together
summary: When a value has to live on the heap, when several owners have to share it, how Rust counts them (Rc on one thread, Arc across threads), what a Weak pointer is for, and how each maps to unique_ptr, shared_ptr and weak_ptr.
minutes: 14
---
Most Rust values live directly in the variable that owns them: an integer on the stack, a struct inside another struct. That is wonderfully cheap, and it stops working in exactly three situations. A type contains itself (a tree node that holds its children). A value has to be too big or too long-lived for the stack (an 8 KiB page). Or several parts of the program must own the same value and the last one out should clean up (a page that many readers hold). The standard library has one tool for each, and they are small enough to learn in an afternoon.

## Box: one owner, on the heap

Try to write a linked list node the obvious way:

```text
struct Node { value: i32, next: Option<Node> }
error[E0072]: recursive type `Node` has infinite size
```

The compiler must know how big a `Node` is, and a `Node` that contains a `Node` that contains a `Node` has no end. The fix is to put the next node *behind a pointer*. A pointer has a fixed size no matter what it points at, so `Option<Box<Node>>` is finite. `Box<T>` is the simplest smart pointer: it allocates `T` on the heap, owns it exclusively, and frees it when the box goes out of scope. It is C++'s `std::unique_ptr<T>` and just as cheap, one pointer wide.

Two details you will use. `Option<Box<T>>` is the same size as a plain pointer, because `None` can be stored as the null pointer (the compiler knows a `Box` is never null); so "an optional child" costs nothing extra. And `Box<dyn Trait>` is how you hold a value whose exact type is chosen at run time, such as one of several disks that all implement the same trait.

The second use is big values. A buffer pool frame is a page, `[u8; 8192]`. A local array of that size sits on the stack; a hundred of them in a `Vec` would not, which is why frames are `Box<[u8; 8192]>`. A word of caution: `Box::new([0u8; 8192])` builds the array on the stack and then moves it, which is fine for 8 KiB and a stack overflow for a few megabytes. For large buffers use `vec![0u8; n].into_boxed_slice()` or just a `Vec<u8>`.

## Rc and Arc: shared ownership by counting

Sometimes there is no single owner. A cached page is held by the query that reads it, by the replacer that tracks it and by the table of loaded pages; it should be freed when the last of them lets go. `Rc<T>` (reference counted) and `Arc<T>` (atomically reference counted) give exactly that: each `clone()` is a new owner and increments a count; each drop decrements it; at zero, the value is freed.

The `clone()` of an `Rc` or `Arc` copies *the pointer and the count*, not the value, so it is cheap, but it is a deliberate act. The idiom is to write `Arc::clone(&page)` and not `page.clone()`, so a reader sees "this is the cheap one".

The difference between the two is one word: **atomic**. `Rc` counts with ordinary integer arithmetic and is therefore only safe on one thread; the compiler enforces that by making `Rc` not `Send`. `Arc` counts with atomic instructions, which are slower (tens of nanoseconds under contention) but safe to share between threads. If you have a single thread, use `Rc`; the moment a value crosses `thread::spawn`, use `Arc`. Neither gives you mutation: a shared value is read-only unless you put something inside that allows it, which is what the next article covers (`Arc<Mutex<T>>` is the standard pair).

## Weak: pointing without owning

If a parent holds an `Rc` to its child and the child holds an `Rc` back to its parent, neither count can reach zero, and both leak. A **cycle** is the one way reference counting fails. `Weak<T>` is a pointer that does not count: you get it with `Rc::downgrade(&rc)`, and to use it you call `.upgrade()`, which returns `Option<Rc<T>>`, `None` if the value has already been freed. Use `Weak` for the back-edge of any structure (a parent pointer, an observer list) and the cycle disappears.

## Deref: the pointer disappears

All of these implement `Deref`, so you rarely write `*`. `page.len()` on an `Arc<Vec<u8>>` calls `Vec::len` directly, and `&*page` or `&page[..]` gives you the inner `&Vec<u8>`/slice when a function wants one. This is the same convenience as C++'s `operator->`.

## Which one

| You need | Use | C++ |
|---|---|---|
| a value on the heap with one owner; a recursive type; a trait object | `Box<T>` | `std::unique_ptr<T>` |
| several owners, one thread | `Rc<T>` | `std::shared_ptr<T>` (but with an atomic count always) |
| several owners, several threads | `Arc<T>` | `std::shared_ptr<T>` |
| a back-pointer that must not keep the value alive | `Weak<T>` | `std::weak_ptr<T>` |
| nothing: a borrowed reference does the job | `&T` | `const T&` |

The last row matters most. Before you reach for `Rc` or `Arc`, ask whether one place can own the value and the others can borrow it. Cloning an `Arc` in a hot loop costs an atomic increment per iteration; passing `&T` costs nothing. In this course, handles and indices (a `usize` into a `Vec`) are often a better answer than shared pointers, because they have no counts and no cycles.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `std::make_unique<T>(...)` | `Box::new(...)` |
| `std::make_shared<T>(...)`; copy the pointer to share | `Arc::new(...)`; `Arc::clone(&a)` |
| `shared_ptr` count is always atomic | `Rc` (not atomic) and `Arc` (atomic) are separate types, and the compiler stops you using the wrong one |
| `weak_ptr::lock()` returns a `shared_ptr` (maybe empty) | `weak.upgrade()` returns `Option<Rc<T>>` |
| a `shared_ptr` cycle leaks silently | the same, and `Weak` is the cure |

**Port rule:** `unique_ptr` is `Box`, `shared_ptr` is `Arc` unless you are sure there is one thread, and every `weak_ptr` is a `Weak`.

## In real code

### Using it: a list, shared counts, a weak parent

```rust test
use std::rc::{Rc, Weak};
use std::sync::Arc;

// A recursive type needs a Box.
#[derive(Debug)]
struct Node {
    value: i32,
    next: Option<Box<Node>>,
}

fn sum(list: &Option<Box<Node>>) -> i32 {
    let mut total = 0;
    let mut cur = list;
    while let Some(node) = cur {
        total += node.value;
        cur = &node.next;
    }
    total
}

// A tree whose children know their parent without owning it.
struct TreeNode {
    name: &'static str,
    parent: std::cell::RefCell<Weak<TreeNode>>,
    children: std::cell::RefCell<Vec<Rc<TreeNode>>>,
}

#[test]
fn a_box_makes_a_recursive_type_possible() {
    let list = Some(Box::new(Node { value: 1, next: Some(Box::new(Node { value: 2, next: Some(Box::new(Node { value: 3, next: None })) })) }));
    assert_eq!(sum(&list), 6);
    // None is stored as the null pointer: an optional Box costs no extra space.
    assert_eq!(std::mem::size_of::<Option<Box<Node>>>(), std::mem::size_of::<Box<Node>>());
}

#[test]
fn rc_counts_owners_and_frees_at_zero() {
    let page = Rc::new(vec![1u8, 2, 3]);
    assert_eq!(Rc::strong_count(&page), 1);
    let reader = Rc::clone(&page);
    assert_eq!(Rc::strong_count(&page), 2);
    assert_eq!(reader.len(), 3, "the pointer derefs to the Vec");
    drop(reader);
    assert_eq!(Rc::strong_count(&page), 1);
}

#[test]
fn a_weak_pointer_breaks_the_parent_child_cycle() {
    let parent = Rc::new(TreeNode { name: "root", parent: Default::default(), children: Default::default() });
    let child = Rc::new(TreeNode { name: "leaf", parent: Default::default(), children: Default::default() });
    *child.parent.borrow_mut() = Rc::downgrade(&parent);
    parent.children.borrow_mut().push(Rc::clone(&child));
    assert_eq!(child.parent.borrow().upgrade().map(|p| p.name), Some("root"));
    assert_eq!(Rc::strong_count(&parent), 1, "the child's pointer to its parent does not count");
    drop(parent);
    assert!(child.parent.borrow().upgrade().is_none(), "the parent is gone: upgrade returns None");
    assert_eq!(child.name, "leaf");
}

#[test]
fn an_arc_crosses_threads() {
    let data = Arc::new((1..=100u64).collect::<Vec<_>>());
    let handles: Vec<_> = (0..4)
        .map(|i| {
            let data = Arc::clone(&data);
            std::thread::spawn(move || data.iter().skip(i * 25).take(25).sum::<u64>())
        })
        .collect();
    let total: u64 = handles.into_iter().map(|h| h.join().unwrap()).sum();
    assert_eq!(total, 5050);
    assert_eq!(Arc::strong_count(&data), 1, "every thread's clone was dropped when it finished");
}
```

### In the exercises

Any stage that shares something: the disk behind an `Arc<dyn DiskIo>` (1a-04, 1b), page frames as boxed arrays (1f), parent and child pointers in a tree (2c, where indices usually do better), and the transaction map of module 4.

### Where it is used

- **Every Rust program with a tree or a graph** (`Box` for ownership edges, `Weak` for back edges).
- **Servers**: configuration or a connection pool shared by `Arc` between request threads.
- **Databases written in Rust** (TiKV, Materialize, DataFusion) pass `Arc<dyn Trait>` for pluggable storage and operators.
