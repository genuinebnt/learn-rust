pub fn append_longest(words: &mut Vec<String>) {
    let shouted = match words.iter().max_by_key(|w| w.len()) {
        Some(longest) => format!("{longest}!"),
        None => return,
    };
    words.push(shouted);
}
