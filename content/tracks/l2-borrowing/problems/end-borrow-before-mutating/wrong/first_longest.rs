pub fn append_longest(words: &mut Vec<String>) {
    let shouted = match words.iter().reduce(|a, b| if b.len() > a.len() { b } else { a }) {
        Some(longest) => format!("{longest}!"),
        None => return,
    };
    words.push(shouted);
}
