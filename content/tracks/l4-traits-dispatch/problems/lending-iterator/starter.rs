use std::marker::PhantomData;

// TODO: the LendingIterator trait. Its `next` returns an item that may borrow from the iterator itself.

/// Overlapping mutable windows of `size`, moving one element at a time.
pub struct WindowsMut<'s, T> {
    // TODO (remove the placeholder)
    _todo: PhantomData<&'s mut T>,
}

/// Panics if `size` is 0.
pub fn windows_mut<T>(slice: &mut [T], size: usize) -> WindowsMut<'_, T> {
    todo!()
}

impl<'s, T> LendingIterator for WindowsMut<'s, T> {
    // TODO: items are `&mut [T]` windows.
}

/// Each line of `text`, trimmed and uppercased, written into one reused buffer.
pub struct UpperLines<'s> {
    // TODO (remove the placeholder)
    _todo: PhantomData<&'s str>,
}

pub fn upper_lines(text: &str) -> UpperLines<'_> {
    todo!()
}

impl<'s> LendingIterator for UpperLines<'s> {
    // TODO: items are `&str` borrowed from the buffer.
}

/// Counts the items of any lending iterator.
pub fn count<L: LendingIterator>(it: L) -> usize {
    todo!()
}
