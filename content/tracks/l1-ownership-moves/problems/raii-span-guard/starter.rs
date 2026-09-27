use std::cell::RefCell;

pub struct Span<'a> {
    name: &'static str,
    log: &'a RefCell<Vec<String>>,
}

impl<'a> Span<'a> {
    pub fn enter(name: &'static str, log: &'a RefCell<Vec<String>>) -> Self {
        todo!()
    }

    /// Ends the span with a status: records "exit <name>: <status>" instead of the plain exit.
    pub fn finish(self, status: &str) {
        todo!()
    }
}

impl Drop for Span<'_> {
    fn drop(&mut self) {
        // TODO: record the exit.
        // (Left empty rather than todo!(): a panic in drop during a failing test aborts every test.)
    }
}
