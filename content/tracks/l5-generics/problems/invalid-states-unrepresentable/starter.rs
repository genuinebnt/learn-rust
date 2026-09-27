use std::marker::PhantomData;

/// A list that can't be empty.
#[derive(Debug, Clone, PartialEq)]
pub struct NonEmpty<T> {
    // Replace this with a representation in which "empty" can't be expressed.
    _todo: PhantomData<T>,
}

/// The error from converting an empty Vec.
#[derive(Debug, PartialEq)]
pub struct Empty;

impl<T> NonEmpty<T> {
    pub fn new(head: T) -> Self {
        todo!()
    }

    pub fn push(&mut self, x: T) {
        todo!()
    }

    /// Removes and returns the last item, unless it's the only one.
    pub fn pop(&mut self) -> Option<T> {
        todo!()
    }

    pub fn first(&self) -> &T {
        todo!()
    }

    pub fn last(&self) -> &T {
        todo!()
    }

    pub fn len(&self) -> usize {
        todo!()
    }

    pub fn get(&self, i: usize) -> Option<&T> {
        todo!()
    }

    pub fn split_first(&self) -> (&T, &[T]) {
        todo!()
    }

    pub fn iter(&self) -> impl Iterator<Item = &T> + '_ {
        // Placeholder so the crate compiles.
        std::iter::empty()
    }

    pub fn map<U>(self, f: impl FnMut(T) -> U) -> NonEmpty<U> {
        todo!()
    }

    /// The largest item; the first of equal largest ones. No Option: there's always one.
    pub fn max(&self) -> &T
    where
        T: Ord,
    {
        todo!()
    }

    pub fn sort(&mut self)
    where
        T: Ord,
    {
        todo!()
    }

    pub fn into_vec(self) -> Vec<T> {
        todo!()
    }
}

impl<T> TryFrom<Vec<T>> for NonEmpty<T> {
    type Error = Empty;

    fn try_from(v: Vec<T>) -> Result<Self, Empty> {
        todo!()
    }
}

impl<T> IntoIterator for NonEmpty<T> {
    type Item = T;
    // Change this to whatever iterator your representation gives.
    type IntoIter = std::vec::IntoIter<T>;

    fn into_iter(self) -> Self::IntoIter {
        todo!()
    }
}
