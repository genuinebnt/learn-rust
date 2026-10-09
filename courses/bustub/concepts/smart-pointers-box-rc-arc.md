---
title: Smart pointers: Box, Rc, Arc and Deref
summary: When one owner is enough, when ownership must be shared, the difference between Rc and Arc, what Deref buys the guard types in this course, and the cycle trap that Weak fixes.
minutes: 8
---
A **smart pointer** owns data behind a pointer and does something when it goes away (free it, decrement a count, release a lock). The standard ones differ in *who owns*:

| pointer | owners | thread-safe | typical use |
|---|---|---|---|
| `Box<T>` | exactly one | if `T` is | heap allocation, recursive types, `Box<dyn Trait>` |
| `Rc<T>` | many, counted | **no** | shared ownership inside one thread |
| `Arc<T>` | many, counted atomically | yes | shared ownership across threads |
| `Weak<T>` | none (a non-owning handle) | like its `Rc`/`Arc` | back-links; breaks cycles |

`Rc` and `Arc` only give **shared, immutable** access (`&T`). To mutate shared data you put a `Mutex`/`RwLock`/atomic inside, or (single-threaded) a `RefCell`: see *interior mutability*.

## Which one

1. Does one place own the value? Then use a plain value or `Box`; do not reach for `Rc` "just in case". An `Rc` when there is a single owner is a classic anti-pattern.
2. Several owners, one thread: `Rc`. Several owners, several threads: `Arc`.
3. Are there parent/child back-references? The back-link is `Weak`, or better, an index (see *arenas*).

This course uses `Arc` 72 times and `Rc` almost never: persistent tries share nodes with `Arc`, plans are `Arc<PlanNode>`, expressions `Arc<dyn Expression>`, transactions are `Arc<Transaction>` held by both the manager and the caller. The cheapness of `Arc::clone` (one atomic increment, no data copied) is why `.clone()` on an `Arc` is idiomatic.

## `Deref`: a pointer that behaves like its target

A type that implements `Deref<Target = T>` lets `*x` and method calls reach the `T`. That is how `Box<T>` and `Arc<T>` feel like the value, and how this course's `ReadPageGuard` feels like the page bytes and `ValueGuard<T>` like a `T`. The legitimate use is *pointer-like wrappers*. Using `Deref` to fake inheritance between unrelated structs is an anti-pattern: use composition or traits.

## Cycles leak, `Weak` breaks them

Two `Rc`s pointing at each other never reach count zero, so neither is freed. Make one direction a `Weak`: it does not keep the target alive, and `upgrade()` returns `None` once the target is gone.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `std::unique_ptr<T>` | `Box<T>` |
| `std::shared_ptr<T>` (atomic count) | `Arc<T>`; the non-atomic `Rc<T>` is the cheaper one for one thread |
| `std::weak_ptr<T>` and `lock()` | `Weak<T>` and `upgrade()` |
| `operator->` and `operator*` | `Deref` (and `DerefMut`) |

**Port rule:** `shared_ptr` becomes `Arc` unless you can prove the data never leaves a thread; `unique_ptr` becomes a plain owned value more often than a `Box`.

## In real code

### Using it: counting owners and breaking a cycle

```rust test
use std::rc::{Rc, Weak};
use std::cell::RefCell;
use std::sync::Arc;

#[test]
fn clones_share_one_value_and_the_count_tracks_the_owners() {
    let a = Arc::new(String::from("shared"));
    let b = Arc::clone(&a);
    assert_eq!(Arc::strong_count(&a), 2);
    assert!(Arc::ptr_eq(&a, &b));
    drop(b);
    assert_eq!(Arc::strong_count(&a), 1);
}

struct Parent {
    children: RefCell<Vec<Rc<Child>>>,
}
struct Child {
    parent: RefCell<Weak<Parent>>,
}

#[test]
fn a_weak_back_link_does_not_keep_the_parent_alive() {
    let child = Rc::new(Child { parent: RefCell::new(Weak::new()) });
    let parent = Rc::new(Parent { children: RefCell::new(vec![child.clone()]) });
    *child.parent.borrow_mut() = Rc::downgrade(&parent);
    assert!(child.parent.borrow().upgrade().is_some());
    assert_eq!(Rc::strong_count(&parent), 1, "the child's link is weak");
    drop(parent);
    assert!(child.parent.borrow().upgrade().is_none(), "the parent is gone, the child survived");
}
```

### Using it: Box for a recursive type, Deref for a guard

```rust test
use std::ops::Deref;

enum Expr {
    Num(i64),
    Add(Box<Expr>, Box<Expr>),
}

fn eval(e: &Expr) -> i64 {
    match e {
        Expr::Num(n) => *n,
        Expr::Add(a, b) => eval(a) + eval(b),
    }
}

struct Guard<T> {
    value: std::sync::Arc<T>,
}

impl<T> Deref for Guard<T> {
    type Target = T;
    fn deref(&self) -> &T {
        &self.value
    }
}

#[test]
fn a_recursive_type_needs_a_box_to_have_a_size() {
    let e = Expr::Add(Box::new(Expr::Num(2)), Box::new(Expr::Add(Box::new(Expr::Num(3)), Box::new(Expr::Num(4)))));
    assert_eq!(eval(&e), 9);
}

#[test]
fn a_guard_that_derefs_reads_like_the_value() {
    let g = Guard { value: std::sync::Arc::new(String::from("page")) };
    assert_eq!(g.len(), 4, "String methods through Deref");
    assert_eq!(&*g, "page");
}
```

### In the exercises

- **0a-02:** path copying shares `Arc<TrieNode>` between versions.
- **0a-04:** `ValueGuard<T>` derefs to its value.
- **3d:** plans and expressions are `Arc` trees; `Box<dyn Executor>` is the executor tree.
- **4a-02:** the manager and the caller both hold an `Arc<Transaction>`.

### Where it is used

- **Everywhere in Rust**: `Box<dyn Error>`, `Arc<Mutex<..>>`, `Rc<RefCell<..>>` in single-threaded UIs, `Cow` and `Weak` for caches and observers.
- The Rust Book chapter 15 is the reference for the table above.
