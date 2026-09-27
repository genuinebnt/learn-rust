use std::marker::PhantomData;

/// Applies `f` to `start` `n` times. Generic: one copy per closure type.
pub fn apply_n<F: FnMut(i64) -> i64>(start: i64, n: u32, f: F) -> i64 {
    todo!()
}

/// The same through a trait object: one copy, called through a vtable.
pub fn apply_n_dyn(start: i64, n: u32, f: &mut dyn FnMut(i64) -> i64) -> i64 {
    todo!()
}

/// Steps run in the order they were pushed. Steps may borrow local state (`'a`), and a whole
/// pipeline can be moved to another thread.
pub struct Pipeline<'a> {
    // TODO: the steps. (Remove this placeholder.)
    _todo: PhantomData<&'a ()>,
}

impl<'a> Pipeline<'a> {
    pub fn new() -> Self {
        todo!()
    }

    pub fn push(&mut self, step: impl FnMut(i64) -> i64 + Send + 'a) -> &mut Self {
        todo!()
    }

    pub fn len(&self) -> usize {
        todo!()
    }

    /// Threads `x` through every step.
    pub fn run(&mut self, x: i64) -> i64 {
        todo!()
    }
}
