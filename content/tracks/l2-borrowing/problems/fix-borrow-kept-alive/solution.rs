/// Uppercases the first name, then appends "!" to every name.
pub fn shout_first(names: &mut Vec<String>) {
    let first = &mut names[0];
    first.make_ascii_uppercase();
    for n in names.iter_mut() {
        n.push('!');
    }
}
