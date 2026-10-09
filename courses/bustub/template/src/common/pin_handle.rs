//! Pins counted by the handles that exist.

use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;

pub struct Pins {
    _pins: (),
}

pub struct PinHandle {
    _handle: (),
}

impl Pins {
    pub fn new() -> Pins {
        todo!("1g-c2: nothing is pinned")
    }

    pub fn pin(&self) -> PinHandle {
        todo!("1g-c2: count one more pin and give out a handle")
    }

    pub fn count(&self) -> usize {
        todo!("1g-c2: the live handles")
    }
}

impl Default for Pins {
    fn default() -> Self {
        Pins::new()
    }
}

impl Clone for PinHandle {
    fn clone(&self) -> PinHandle {
        todo!("1g-c2: a clone is another pin")
    }
}

impl Drop for PinHandle {
    fn drop(&mut self) {
        // TODO(1g-c2): uncount this pin
    }
}
