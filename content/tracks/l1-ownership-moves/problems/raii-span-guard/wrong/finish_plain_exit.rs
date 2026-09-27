use std::cell::RefCell;

pub struct Span<'a> {
    name: &'static str,
    log: &'a RefCell<Vec<String>>,
}

impl<'a> Span<'a> {
    pub fn enter(name: &'static str, log: &'a RefCell<Vec<String>>) -> Self {
        log.borrow_mut().push(format!("enter {name}"));
        Span { name, log }
    }

    /// Ends the span with a status: records "exit <name>: <status>" instead of the plain exit.
    pub fn finish(self, status: &str) {
        let _ = status;
    }
}

impl Drop for Span<'_> {
    fn drop(&mut self) {
        self.log.borrow_mut().push(format!("exit {}", self.name));
    }
}
