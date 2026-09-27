pub fn greet(name: &str) -> String {
    format!("Hello, {name}!")
}

pub fn exclaim(s: &mut String) {
    s.push('!');
}

pub fn first_word(s: &str) -> &str {
    s.split_whitespace().next().unwrap_or("")
}
