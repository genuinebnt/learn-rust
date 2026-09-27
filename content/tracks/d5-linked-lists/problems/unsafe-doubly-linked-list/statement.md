Implement the same list with raw `NonNull` pointers: nodes are allocated with `Box` and owned by the list.
Write a `// SAFETY:` comment on every `unsafe` block. `iter` yields `&i32` tied to the list's lifetime, and
dropping the list frees every node without recursion. (Best attempted after Y2 Unsafe Rust.)
