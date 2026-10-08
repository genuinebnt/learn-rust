**Where this fits.** Most callers (an index, a table heap) have already made sure there is room: running out of frames is a bug for them, not a case to handle.

## The task

In `src/buffer/buffer_pool_manager.rs`: `read_page(page_id)` and `write_page(page_id)` do what `checked_read_page` / `checked_write_page` do, but return the guard itself and **panic** (message containing "every frame is pinned") if the page can't be brought in.

## Tests

- With room, both return a guard (two guards on the same page give pin count 2).
- In a one-frame pool with the frame pinned, both panic with the message.

## Syntax and methods

```rust
self.checked_read_page(page_id).expect("every frame is pinned: no room to bring the page into memory")
```

## Notes

**Two APIs, one meaning.** `Option` for "the caller can recover" and a panic for "the caller can't": BusTub has both (`CheckedReadPage`/`ReadPage`) because C++ code often wraps the former in a throwing check. In Rust, the convention is `try_*`/`checked_*` returning `Option`/`Result` and the plain name panicking (compare `Vec::get` and indexing, `checked_add` and `+`).

## In BusTub

```cpp
auto BufferPoolManager::ReadPage(page_id_t page_id, AccessType access_type) -> ReadPageGuard {
  auto guard_opt = CheckedReadPage(page_id, access_type);
  if (!guard_opt.has_value()) { fmt::println(stderr, "\n`CheckedReadPage` failed to bring in page {}\n", page_id); std::abort(); }
  return std::move(guard_opt).value();
}
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::abort()` after printing to stderr | `panic!` / `expect`: unwinds (running destructors, poisoning locks) instead of killing the process |
| `std::move(guard_opt).value()` | `.expect(..)` / `.unwrap()` moves the guard out |
| `fmt::println(stderr, ...)` | the panic message |

**Port rule:** `abort()` on an impossible condition is `panic!`/`unwrap`/`expect`; use `process::abort()` only when unwinding itself would be unsafe.

## Learn more
- The Rust Book: [`unwrap` and `expect`](https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html#shortcuts-for-panic-on-error-unwrap-and-expect) · [`Option::expect`](https://doc.rust-lang.org/std/option/enum.Option.html#method.expect)
