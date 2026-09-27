use std::collections::HashSet;

pub fn find_all_concatenated_words<'a>(words: &[&'a str]) -> Vec<&'a str> {
    let set: HashSet<&str> = words.iter().copied().filter(|w| !w.is_empty()).collect();
    words.iter().copied().filter(|w| (1..w.len()).any(|k| set.contains(&w[..k]) && set.contains(&w[k..]))).collect()
}
