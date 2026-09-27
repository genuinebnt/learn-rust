pub fn initials(full_name: &str) -> String {
    full_name
        .split(' ')
        .filter_map(|w| w.chars().next())
        .flat_map(char::to_uppercase)
        .collect()
}
