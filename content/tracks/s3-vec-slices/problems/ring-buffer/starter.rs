pub struct Ring<T> {
    buf: Box<[Option<T>]>,
    head: usize,
    len: usize,
}

impl<T> Ring<T> {
    /// Panics if `capacity` is 0.
    pub fn with_capacity(capacity: usize) -> Self {
        todo!()
    }

    /// Adds `value`, returning the evicted oldest value if the ring was full.
    pub fn push(&mut self, value: T) -> Option<T> {
        todo!()
    }

    pub fn len(&self) -> usize {
        todo!()
    }

    pub fn iter(&self) -> impl Iterator<Item = &T> + '_ {
        std::iter::empty() // TODO
    }
}
