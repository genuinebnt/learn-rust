use std::collections::HashSet;

fn splits(set: &HashSet<&str>, w: &str, start: usize, pieces: usize) -> bool {
    if start == w.len() {
        return pieces >= 2;
    }
    (start + 1..=w.len()).any(|end| set.contains(&w[start..end]) && splits(set, w, end, pieces + 1))
}

pub fn find_all_concatenated_words<'a>(words: &[&'a str]) -> Vec<&'a str> {
    let set: HashSet<&str> = words.iter().copied().filter(|w| !w.is_empty()).collect();
    words.iter().copied().filter(|w| !w.is_empty() && splits(&set, w, 0, 0)).collect()
}
