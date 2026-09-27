pub struct Pairs<'a, T> {
    rest: &'a [T],
}

pub fn pairs<T>(v: &[T]) -> Pairs<'_, T> {
    Pairs { rest: v }
}

impl<'a, T> Iterator for Pairs<'a, T> {
    type Item = (&'a T, &'a T);

    fn next(&mut self) -> Option<Self::Item> {
        match self.rest {
            [a, b, rest @ ..] => {
                self.rest = rest;
                Some((a, b))
            }
            _ => None,
        }
    }

    fn size_hint(&self) -> (usize, Option<usize>) {
        let n = (self.rest.len() + 1) / 2;
        (n, Some(n))
    }
}

impl<T> ExactSizeIterator for Pairs<'_, T> {}
