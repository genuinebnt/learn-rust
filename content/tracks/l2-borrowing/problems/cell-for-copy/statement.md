Each `Node` counts its visits through a shared `&Node`. Use `Cell<u32>`; no `RefCell`, no `&mut`.
