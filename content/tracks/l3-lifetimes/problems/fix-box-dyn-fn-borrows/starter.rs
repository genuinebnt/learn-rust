/// A predicate that accepts exactly the words in `allowed`.
pub fn make_filter(allowed: &[&str]) -> Box<dyn Fn(&str) -> bool> {
    Box::new(move |w| allowed.iter().any(|&a| a == w))
}
