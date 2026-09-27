/// Every `step`-th element of a slice, starting with the first, handed out as `&mut`.
pub struct StepMut<'a, T> {
    rest: &'a mut [T],
    step: usize,
}

/// `v[0], v[step], v[2 * step], ...` as `&mut`. Panics if `step` is 0.
pub fn step_mut<T>(v: &mut [T], step: usize) -> StepMut<'_, T> {
    assert!(step > 0, "step must be positive");
    StepMut { rest: v, step }
}

impl<'a, T> Iterator for StepMut<'a, T> {
    type Item = &'a mut T;

    fn next(&mut self) -> Option<&'a mut T> {
        todo!()
    }

    /// Exact: how many elements are left.
    fn size_hint(&self) -> (usize, Option<usize>) {
        todo!()
    }
}

impl<T> DoubleEndedIterator for StepMut<'_, T> {
    fn next_back(&mut self) -> Option<Self::Item> {
        todo!()
    }
}

impl<T> ExactSizeIterator for StepMut<'_, T> {}
