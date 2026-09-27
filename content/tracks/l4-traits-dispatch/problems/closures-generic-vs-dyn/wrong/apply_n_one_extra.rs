/// Applies `f` to `start` `n` times. Generic: one copy per closure type.
pub fn apply_n<F: FnMut(i64) -> i64>(start: i64, n: u32, mut f: F) -> i64 {
    let mut x = start;
    for _ in 0..=n {
        x = f(x);
    }
    x
}

/// The same through a trait object: one copy, called through a vtable.
pub fn apply_n_dyn(start: i64, n: u32, f: &mut dyn FnMut(i64) -> i64) -> i64 {
    let mut x = start;
    for _ in 0..n {
        x = f(x);
    }
    x
}

/// Steps run in the order they were pushed. Steps may borrow local state (`'a`), and a whole
/// pipeline can be moved to another thread.
pub struct Pipeline<'a> {
    steps: Vec<Box<dyn FnMut(i64) -> i64 + Send + 'a>>,
}

impl<'a> Pipeline<'a> {
    pub fn new() -> Self {
        Pipeline { steps: Vec::new() }
    }

    pub fn push(&mut self, step: impl FnMut(i64) -> i64 + Send + 'a) -> &mut Self {
        self.steps.push(Box::new(step));
        self
    }

    pub fn len(&self) -> usize {
        self.steps.len()
    }

    /// Threads `x` through every step.
    pub fn run(&mut self, x: i64) -> i64 {
        self.steps.iter_mut().fold(x, |acc, step| step(acc))
    }
}
