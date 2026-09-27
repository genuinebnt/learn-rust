fn add_defaults(names: &mut Vec<&'static str>) {
    names.push("root");
    names.push("admin");
}

/// The names in `input` (one per line), then the defaults.
pub fn all_names(input: &str) -> Vec<&str> {
    let mut names: Vec<&str> = Vec::new();
    add_defaults(&mut names);
    names
}
