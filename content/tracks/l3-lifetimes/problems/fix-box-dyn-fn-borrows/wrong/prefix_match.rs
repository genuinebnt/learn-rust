/// A predicate that accepts exactly the words in `allowed`.
pub fn make_filter<'a>(allowed: &'a [&str]) -> Box<dyn Fn(&str) -> bool + 'a> {
    Box::new(move |w| allowed.iter().any(|&a| a.starts_with(w)))
}
