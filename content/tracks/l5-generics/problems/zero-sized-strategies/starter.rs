use std::cmp::Ordering;
use std::marker::PhantomData;

/// How to order items. Implementors are zero-sized: the strategy lives in the type, not in the value.
pub trait Order {
    fn cmp<T: Ord>(a: &T, b: &T) -> Ordering;
}

pub struct Asc;
pub struct Desc;

impl Order for Asc {
    fn cmp<T: Ord>(a: &T, b: &T) -> Ordering {
        todo!()
    }
}

impl Order for Desc {
    fn cmp<T: Ord>(a: &T, b: &T) -> Ordering {
        todo!()
    }
}

/// Items kept sorted by `O`, ascending unless you say otherwise.
pub struct SortedVec<T, O = Asc> {
    items: Vec<T>,
    order: PhantomData<O>,
}

impl<T: Ord, O: Order> SortedVec<T, O> {
    pub fn new() -> Self {
        todo!()
    }

    /// Inserts `x` after any items that compare equal to it.
    pub fn insert(&mut self, x: T) {
        todo!()
    }

    /// Whether some item compares equal to `x` under `O`.
    pub fn contains(&self, x: &T) -> bool {
        todo!()
    }

    pub fn as_slice(&self) -> &[T] {
        todo!()
    }

    /// The same items sorted by another order; equal items keep their relative order.
    pub fn reorder<O2: Order>(self) -> SortedVec<T, O2> {
        todo!()
    }
}

impl<T: Ord, O: Order> FromIterator<T> for SortedVec<T, O> {
    fn from_iter<I: IntoIterator<Item = T>>(iter: I) -> Self {
        todo!()
    }
}
