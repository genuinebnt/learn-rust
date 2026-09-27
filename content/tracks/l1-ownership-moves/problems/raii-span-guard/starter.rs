use std::cell::RefCell;

pub struct Span<'a> {
    name: &'static str,
    log: &'a RefCell<Vec<String>>,
}

impl<'a> Span<'a> {
    pub fn enter(name: &'static str, log: &'a RefCell<Vec<String>>) -> Self {
        todo!()
    }
}

impl Drop for Span<'_> {
    fn drop(&mut self) {
        // TODO: record the exit.
        // (Left empty rather than todo!(): a panic in drop during a failing test aborts every test.)
    }
}
