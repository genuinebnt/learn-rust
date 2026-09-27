pub fn append_longest(words: &mut Vec<String>) {
    let longest = words.iter().max_by_key(|w| w.len()).map_or("", |w| w.as_str());
    let shouted = format!("{longest}!");
    words.push(shouted);
}
