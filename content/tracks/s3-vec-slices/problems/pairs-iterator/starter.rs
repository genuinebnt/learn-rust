pub struct Pairs<'a, T> {
    rest: &'a [T],
}

pub fn pairs<T>(v: &[T]) -> Pairs<'_, T> {
    Pairs { rest: v }
}

impl<'a, T> Iterator for Pairs<'a, T> {
    type Item = (&'a T, &'a T);

    fn next(&mut self) -> Option<Self::Item> {
        todo!()
    }

    // TODO: an exact size_hint, so that len() below works.
}

impl<T> ExactSizeIterator for Pairs<'_, T> {}
