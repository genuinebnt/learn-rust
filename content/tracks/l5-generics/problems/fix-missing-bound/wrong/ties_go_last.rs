/// The largest item; the first one on a tie. None if `items` is empty.
pub fn largest<T: PartialOrd>(items: &[T]) -> Option<&T> {
    let mut best = items.first()?;
    for item in items {
        if item >= best {
            best = item;
        }
    }
    Some(best)
}
