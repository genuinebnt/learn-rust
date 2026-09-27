use std::any::{Any, TypeId};
use std::collections::HashMap;
use std::fmt::Debug;

/// Holds at most one value of each type, like `http::Extensions`. Values of any type that owns its data (or
/// borrows only `'static` data) can go in.
pub struct Extensions {
    map: HashMap<TypeId, Box<dyn Any>>,
}

// TODO: impl Extensions.

/// Keeps `value` in `log` for debug output later.
pub fn remember<T: Debug>(log: &mut Vec<Box<dyn Debug>>, value: T) {
    log.push(Box::new(value));
}

/// A name made at run time that lives for the rest of the program. Each call leaks its String on purpose.
pub fn intern_forever(name: String) -> &'static str {
    Box::leak(name.into_boxed_str())
}
