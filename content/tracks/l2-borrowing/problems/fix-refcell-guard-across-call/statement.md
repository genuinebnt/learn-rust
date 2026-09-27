`Bus` compiles, but a listener that subscribes another listener panics, and so does `replay`. Both call
out while holding a `RefCell` guard that the callee needs. Fix them. You may change how listeners are
stored. Listeners must stay free to emit and subscribe from inside a call, with the semantics in the
doc comments.
