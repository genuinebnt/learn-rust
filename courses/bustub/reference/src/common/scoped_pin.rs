//! A pin that is uncounted when dropped, or earlier by `release`.

use std::cell::Cell;

pub struct ScopedPin<'a> {
    counter: &'a Cell<usize>,
}

impl<'a> ScopedPin<'a> {
    pub fn new(counter: &'a Cell<usize>) -> ScopedPin<'a> {
        counter.set(counter.get() + 1);
        ScopedPin { counter }
    }

    /// Uncounts the pin now and returns the count after that.
    pub fn release(self) -> usize {
        // @begin 1g-c3
        let counter = self.counter;
        std::mem::forget(self);
        counter.set(counter.get() - 1);
        counter.get()
        //~ self.counter.set(self.counter.get() - 1);
        //~ self.counter.get()
        // @end
    }
}

impl Drop for ScopedPin<'_> {
    fn drop(&mut self) {
        self.counter.set(self.counter.get() - 1);
    }
}
