/// Moves the first name out, leaving "" in its place.
pub fn take_first(names: &mut Vec<String>) -> String {
    std::mem::take(&mut names[0])
}
