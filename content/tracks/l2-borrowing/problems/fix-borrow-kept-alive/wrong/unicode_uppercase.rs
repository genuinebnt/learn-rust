/// Uppercases the first name, then appends "!" to every name.
pub fn shout_first(names: &mut Vec<String>) {
    for n in names.iter_mut() {
        n.push('!');
    }
    names[0] = names[0].to_uppercase();
}
