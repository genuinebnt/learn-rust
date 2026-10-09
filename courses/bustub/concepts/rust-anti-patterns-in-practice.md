---
title: Rust anti-patterns, seen in real code
summary: A checklist of the habits that make Rust code slow, fragile or hard to read (clone to silence the borrow checker, unwrap, Rc where one owner will do, index loops, public fields with rules, locks held too long), each with what to write instead and where this course avoids it.
minutes: 8
---
Most Rust anti-patterns come from carrying a habit over from another language. The list below follows the `rust-skills` anti-pattern guide; for each, the better form, and a place in this course's code where you can see it done.

| anti-pattern | write instead | in this course |
|---|---|---|
| `.clone()` to make the borrow checker quiet | borrow, restructure ownership, or share with `Arc` | batches clone `Tuple`s on purpose; plans/expressions are `Arc` clones (a counter bump) |
| `.unwrap()` on a fallible call | `?`, `match`, or `expect("why this cannot fail")` | 112 `lock().unwrap()` follow a stated policy (*lock poisoning*); I/O and parsing return `Result` |
| `Rc` when there is one owner | plain ownership, a reference, or `Box` | `Rc` is never used; shared things are `Arc` |
| `unsafe` for convenience | find the safe pattern; confine real `unsafe` to a small wrapper | 0 `unsafe` in the reference |
| `Deref` to fake inheritance | composition, traits | `Deref` only on pointer-like guards |
| index loops `for i in 0..v.len()` | iterators, `enumerate`, `windows`, `zip` | executors and sketches use iterator chains |
| many `pub` fields that carry rules | private fields, a validating constructor | `Transaction` hides its state behind methods; plain data records (`UndoLog`) are deliberately public |
| a bool or `Option` for each state | an `enum` or typestate | `TransactionState`, `Slot::{Empty, Tombstone, Live}` |
| `String` parameters everywhere | `&str` (or `impl AsRef<str>`), `Cow<str>` when a copy is sometimes needed | lookups take `&str` |
| giant `match` arms | extract helpers, or a trait with one method per case | the planner/binder split cases into functions |
| deep nesting and long functions | early returns (`?`, `let-else`), small functions | `modify_tuple` uses early returns for the conflict |
| custom pointer linked lists | `Vec`, `VecDeque`, or an arena with index links | the replacer list and the skip list are arenas |
| `lazy_static!`/`static mut` | `std::sync::OnceLock`, `LazyLock` | no global mutable state |
| `mem::transmute` | `as`, `TryFrom`, `from_le_bytes` | pages are read with `from_le_bytes` |
| ignoring `#[must_use]` results | handle or `let _ =` with a comment | results of `Result`-returning calls are propagated |
| holding a lock across a call you don't control | copy out what you need, drop the guard, then call | the trie store clones the root and works outside the lock |
| `Arc<Mutex<T>>` everywhere | message passing, atomics, or a narrower lock | atomics for counters; one `RwLock` where reads dominate |

## How to use the list

Treat each row as a question to ask in review, not a rule to obey: `clone()` is correct when you really need two owned copies, a `pub` field is fine for a plain data record, and `unwrap()` is fine where the type or an earlier check proves it. What the list gives you is the habit of asking *why* before writing the shortcut. When the compiler pushes back (E0382 use after move, E0499 two mutable borrows, E0502 a borrow while another lives), the usual fix is a change of design, not a `clone()`.

## C++ comparison

| C / C++ habit | what it becomes in Rust |
|---|---|
| copy to be safe | move or borrow; copy only when two owners are the point |
| `shared_ptr` by default | a single owner by default |
| raw pointer for a back-link | an index, or `Weak` |
| `static` global state | a value passed in, or `OnceLock` |

**Port rule:** start from "who owns this?" rather than "how do I make the compiler accept this?".

## In real code

### Using it: three rewrites

```rust test
// 1. clone to dodge the borrow checker  ->  restructure so nothing needs it
fn longest_clone(words: &[String]) -> String {
    let mut best = String::new();
    for w in words {
        if w.len() > best.len() {
            best = w.clone();
        }
    }
    best
}
fn longest_borrow(words: &[String]) -> Option<&String> {
    words.iter().max_by_key(|w| w.len())
}

// 2. index loop  ->  iterator
fn sum_even_index_loop(v: &[i32]) -> i32 {
    let mut total = 0;
    for i in 0..v.len() {
        if v[i] % 2 == 0 {
            total += v[i];
        }
    }
    total
}
fn sum_even(v: &[i32]) -> i32 {
    v.iter().filter(|x| **x % 2 == 0).sum()
}

#[test]
fn borrowing_returns_the_same_answer_without_copying() {
    let words: Vec<String> = ["ab", "abcd", "abc"].iter().map(|s| s.to_string()).collect();
    assert_eq!(longest_clone(&words), "abcd");
    assert_eq!(longest_borrow(&words).map(|s| s.as_str()), Some("abcd"));
}

#[test]
fn the_iterator_form_is_shorter_and_cannot_index_out_of_range() {
    let v = [1, 2, 3, 4, 6];
    assert_eq!(sum_even_index_loop(&v), sum_even(&v));
    assert_eq!(sum_even(&v), 12);
}
```

### Using it: a bool state, an enum state, and a lock held too long

```rust test
use std::sync::Mutex;

// a pair of bools allows 4 states, 1 of them meaningless
struct BadTxn { running: bool, committed: bool }
// an enum allows exactly the legal ones
#[derive(Debug, PartialEq, Clone, Copy)]
enum State { Running, Committed, Aborted }

#[test]
fn an_enum_makes_the_impossible_state_unrepresentable() {
    let nonsense = BadTxn { running: true, committed: true };
    assert!(nonsense.running && nonsense.committed, "the bool version can say both");
    let s = State::Committed;
    assert_ne!(s, State::Running);
    let _ = (State::Aborted, State::Running);
}

fn slow_square(n: u64) -> u64 { (0..n).map(|_| n).sum() }

#[test]
fn copy_out_then_work_outside_the_lock() {
    let shared = Mutex::new(vec![10u64, 20, 30]);
    // bad: slow_square runs while the guard is alive and blocks every other thread
    // good: take what you need, let the guard drop, then compute
    let snapshot = shared.lock().unwrap().clone();
    let squares: Vec<u64> = snapshot.iter().map(|n| slow_square(*n)).collect();
    shared.lock().unwrap().push(squares[0]);
    assert_eq!(*shared.lock().unwrap().last().unwrap(), 100);
}
```

### In the exercises

- **1f:** the buffer pool drops its latch before waiting on the disk.
- **3f / 3g:** executors clone tuples into batches deliberately, and nothing else.
- **4b-02:** `modify_tuple` is early returns, not nesting.
- **0a-04:** the store does its work outside the root lock.

### Where it is used

- The Rust API Guidelines and clippy's lint groups (`clippy::pedantic`, `needless_range_loop`, `clone_on_copy`, `unwrap_used`) encode most of this table; running `cargo clippy` on the reference is a good habit.
