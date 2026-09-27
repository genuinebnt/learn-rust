pub fn reverse_each_word(s: &str) -> String {
    s.split(' ')
        .map(|w| w.chars().rev().collect::<String>())
        .collect::<Vec<_>>()
        .join(" ")
}
