use std::cell::RefCell;

pub struct Span<'a> {
    name: &'static str,
    log: &'a RefCell<Vec<String>>,
}

impl<'a> Span<'a> {
    pub fn enter(name: &'static str, log: &'a RefCell<Vec<String>>) -> Self {
        log.borrow_mut().push(format!("enter {name}"));
        log.borrow_mut().push(format!("exit {name}"));
        Span { name, log }
    }
}

impl Drop for Span<'_> {
    fn drop(&mut self) {
        let _ = (self.name, self.log);
    }
}
