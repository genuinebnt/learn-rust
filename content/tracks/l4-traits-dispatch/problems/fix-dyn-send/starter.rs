use std::cell::Cell;
use std::rc::Rc;
use std::thread;

pub trait Handler {
    /// A reply to `event`, or None.
    fn handle(&self, event: &str) -> Option<String>;
}

/// Counts the events it sees. Whoever holds a clone of `count` can read it.
pub struct Counter {
    pub count: Rc<Cell<usize>>,
}

impl Handler for Counter {
    fn handle(&self, _event: &str) -> Option<String> {
        self.count.set(self.count.get() + 1);
        None
    }
}

/// Replies with `prefix` + the event.
pub struct Echo {
    pub prefix: String,
}

impl Handler for Echo {
    fn handle(&self, event: &str) -> Option<String> {
        Some(format!("{}{}", self.prefix, event))
    }
}

#[derive(Default)]
pub struct Bus {
    handlers: Vec<Box<dyn Handler>>,
}

impl Bus {
    pub fn register(&mut self, h: Box<dyn Handler>) {
        self.handlers.push(h);
    }

    /// For each event in order, every handler's reply in registration order.
    pub fn dispatch(&self, events: &[&str]) -> Vec<String> {
        let mut out = Vec::new();
        for e in events {
            for h in &self.handlers {
                out.extend(h.handle(e));
            }
        }
        out
    }
}

/// Dispatches on a worker thread.
pub fn dispatch_in_background(bus: Bus, events: Vec<String>) -> Vec<String> {
    thread::spawn(move || {
        let refs: Vec<&str> = events.iter().map(String::as_str).collect();
        bus.dispatch(&refs)
    })
    .join()
    .unwrap()
}
