---
title: Modules, visibility and API boundaries
summary: How mod and use organise a crate, what pub, pub(crate) and private mean, how re-exports shape the public API, and how this course's hidden-module trick relies on mod.rs files that only declare.
minutes: 6
---
A Rust **crate** is a tree of **modules**. `mod disk_manager;` in `storage/disk/mod.rs` says "there is a module here, in `disk_manager.rs`"; `use crate::storage::disk::disk_manager::DiskManager;` brings a name into scope. Everything is **private to its module by default**; you open things up deliberately:

| visibility | who can see it |
|---|---|
| (none) | the module it is in, and that module's children |
| `pub(super)` | the parent module |
| `pub(crate)` | anywhere in this crate, but not users of the crate |
| `pub` | anyone who can reach the module path |
| `pub use inner::Thing;` | a **re-export**: `Thing` appears at this path too |

Fields have their own visibility: a struct can be `pub` with private fields (users cannot construct it or read its fields except through your methods), which is how a type keeps an invariant (see *newtypes*).

## Boundaries on purpose

- Keep implementation details private or `pub(crate)`: this course marks the transaction's state setters `pub(crate)` so that only the manager (in the same crate) can change a transaction's state, while tests, which are outside the crate, can only read it.
- Put the public face in one place with re-exports, so internal reorganisation does not break users.
- A test directory (`tests/*.rs`) is a separate crate that sees only the **public** API: it is a check that the API is usable, and it is why helper methods for tests (`Watermark`'s accessors, `HyperLogLog::registers`) are `pub`.

## How the hidden-module mechanism uses this

A learner's repo contains only the modules they have unlocked. The template builder keeps a `mod.rs` or `lib.rs` that consists **only of `mod`/`pub mod` declarations** and removes the lines for files that are not there yet; a `mod.rs` that also contains code is always kept whole. That is why the course keeps `mod.rs` files as bare declaration lists, and why a new given file must be listed in a module's `files`: otherwise it would appear from the first module and reference code that does not exist yet.

## C++ comparison

| C / C++ | Rust |
|---|---|
| headers and translation units, `#include` | one tree of modules; `use` imports names, no textual inclusion |
| `private:` / `public:` per member | private by default per item; fields have their own `pub` |
| `friend` classes | `pub(crate)` / `pub(super)`, or putting both types in one module |
| anonymous namespace | a private item |
| `namespace` re-opened in many files | one module per file, `pub use` to flatten |

**Port rule:** a header's public declarations become `pub` items in a module; everything else stays private.

## In real code

### Using it: a module with a private field and pub(crate) access

```rust test
mod account {
    pub struct Account {
        balance: i64, // private: only this module can change it
    }
    impl Account {
        pub fn new() -> Account {
            Account { balance: 0 }
        }
        pub fn deposit(&mut self, n: i64) {
            assert!(n > 0, "deposits are positive");
            self.balance += n;
        }
        pub fn balance(&self) -> i64 {
            self.balance
        }
        /// Visible to the rest of the crate (tests inside it) but not to downstream users.
        pub(crate) fn reset(&mut self) {
            self.balance = 0;
        }
    }
}

use account::Account;

#[test]
fn outside_code_goes_through_the_methods() {
    let mut a = Account::new();
    a.deposit(5);
    assert_eq!(a.balance(), 5);
    // a.balance = 100; would not compile: the field is private
    a.reset();
    assert_eq!(a.balance(), 0);
}

#[test]
fn a_violated_rule_is_stopped_at_the_only_door() {
    let mut a = Account::new();
    assert!(std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| a.deposit(-1))).is_err());
}
```

### Using it: re-exports flatten the path

```rust test
mod storage {
    pub mod disk {
        pub mod disk_manager {
            pub struct DiskManager(pub u32);
        }
        pub use self::disk_manager::DiskManager; // re-export
    }
}

use storage::disk::DiskManager; // the short path works because of the re-export

#[test]
fn both_paths_name_the_same_type() {
    let a = DiskManager(3);
    let b: storage::disk::disk_manager::DiskManager = DiskManager(4);
    assert_eq!(a.0 + b.0, 7);
}

#[test]
fn private_means_private_to_the_module_and_its_children() {
    mod outer {
        fn secret() -> u8 { 7 }
        pub mod inner {
            pub fn peek() -> u8 { super::secret() } // a child may use its parent's private items
        }
    }
    assert_eq!(outer::inner::peek(), 7);
}
```

### In the exercises

- **1a:** the module layout mirrors BusTub's directories (`storage/disk/disk_manager.rs`).
- **4a-02:** `set_state`, `set_read_ts` are `pub(crate)`; tests read through `state()`.
- **Every module:** `mod.rs` files only declare their children, which is what lets the next module appear without editing yours.

### Where it is used

- Every crate: the standard library re-exports from private modules (`std::collections::HashMap` lives in `std::collections::hash::map`); the API Guidelines recommend private fields with accessor methods.
