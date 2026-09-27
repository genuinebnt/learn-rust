use std::sync::Arc;

#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord)]
pub enum Level {
    Debug,
    Info,
    Warn,
    Error,
}

pub trait Logger {
    fn log(&self, level: Level, msg: &str);

    /// Pushes out anything buffered. Does nothing by default; every wrapper must pass it on.
    fn flush(&self) {}
}

/// A logger that can be shared across threads.
pub type BoxLogger = Box<dyn Logger + Send + Sync>;

/// Prepends `prefix` to every message.
pub struct PrefixLogger {
    // TODO
}

impl PrefixLogger {
    pub fn new(prefix: &str, inner: BoxLogger) -> Self {
        todo!()
    }
}

impl Logger for PrefixLogger {
    fn log(&self, level: Level, msg: &str) {
        todo!()
    }
}

/// Drops messages below `min`.
pub struct LevelFilter {
    // TODO
}

impl LevelFilter {
    pub fn new(min: Level, inner: BoxLogger) -> Self {
        todo!()
    }
}

impl Logger for LevelFilter {
    fn log(&self, level: Level, msg: &str) {
        todo!()
    }
}

/// Sends every message to all its sinks, in order.
pub struct Tee {
    // TODO
}

impl Tee {
    pub fn new(sinks: Vec<BoxLogger>) -> Self {
        todo!()
    }
}

impl Logger for Tee {
    fn log(&self, level: Level, msg: &str) {
        todo!()
    }
}

/// Lets one logger be shared by several wrappers.
impl<L: Logger + ?Sized> Logger for Arc<L> {
    fn log(&self, level: Level, msg: &str) {
        todo!()
    }
}
