//! A one-shot promise and future: C++'s `std::promise<T>` / `std::future<T>`, which the disk scheduler uses to tell the caller
//! "your request is done". One side sets a value once; the other waits for it.

use std::sync::{Arc, Condvar, Mutex, PoisonError};

enum State<T> {
    Pending,
    Ready(T),
    /// The promise was dropped without a value.
    Broken,
    /// The future has taken the value.
    Taken,
}

struct Shared<T> {
    state: Mutex<State<T>>,
    changed: Condvar,
}

/// The promise was dropped before it set a value: the future will never get one. (C++: `std::future_error`, `broken_promise`.)
#[derive(Debug, PartialEq, Eq)]
pub struct BrokenPromise;

/// The setting side. `set` consumes it, so a value can be set at most once.
pub struct Promise<T> {
    shared: Arc<Shared<T>>,
}

/// The waiting side. `get` consumes it, so a value can be taken at most once.
pub struct Future<T> {
    shared: Arc<Shared<T>>,
}

/// A connected promise and future.
pub fn promise<T>() -> (Promise<T>, Future<T>) {
    let shared = Arc::new(Shared { state: Mutex::new(State::Pending), changed: Condvar::new() });
    (Promise { shared: Arc::clone(&shared) }, Future { shared })
}

impl<T> Promise<T> {
    /// Gives the future its value and wakes it.
    pub fn set(self, value: T) {
        todo!("1b-01: store the value as Ready, then wake whoever waits on `changed`")
    }
}

impl<T> Drop for Promise<T> {
    fn drop(&mut self) {
        // TODO(1b-02): if no value was ever set, mark the promise Broken and wake the future
    }
}

impl<T> Future<T> {
    /// True once `get` would return without waiting: the value is set, or the promise is broken.
    pub fn is_ready(&self) -> bool {
        !matches!(*self.shared.state.lock().unwrap(), State::Pending)
    }

    /// Waits for the value. `Err(BrokenPromise)` if the promise was dropped without setting one.
    pub fn get(self) -> Result<T, BrokenPromise> {
        todo!("1b-01: wait while the state is Pending, then take the state out and return the value")
    }
}
