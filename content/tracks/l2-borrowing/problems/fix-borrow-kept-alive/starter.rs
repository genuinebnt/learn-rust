/// Uppercases the first name, then appends "!" to every name.
pub fn shout_first(names: &mut Vec<String>) {
    let first = &mut names[0];
    for n in names.iter_mut() {
        n.push('!');
    }
    first.make_ascii_uppercase();
}
