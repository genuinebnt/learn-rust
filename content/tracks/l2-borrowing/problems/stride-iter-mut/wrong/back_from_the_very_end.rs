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
        let rest = std::mem::take(&mut self.rest);
        let (first, tail) = rest.split_first_mut()?;
        let skip = (self.step - 1).min(tail.len());
        self.rest = &mut tail[skip..];
        Some(first)
    }

    /// Exact: how many elements are left.
    fn size_hint(&self) -> (usize, Option<usize>) {
        let n = self.rest.len().div_ceil(self.step);
        (n, Some(n))
    }
}

impl<T> DoubleEndedIterator for StepMut<'_, T> {
    fn next_back(&mut self) -> Option<Self::Item> {
        let rest = std::mem::take(&mut self.rest);
        if rest.is_empty() {
            return None;
        }
        let last = rest.len() - 1;
        let (init, tail) = rest.split_at_mut(last);
        self.rest = init;
        tail.first_mut()
    }
}

impl<T> ExactSizeIterator for StepMut<'_, T> {}
