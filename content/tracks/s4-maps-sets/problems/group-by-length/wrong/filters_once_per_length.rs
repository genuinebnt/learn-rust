use std::collections::{HashMap, HashSet};

pub fn group_by_len<'a>(words: &[&'a str]) -> HashMap<usize, Vec<&'a str>> {
    let lengths: HashSet<usize> = words.iter().map(|w| w.len()).collect();
    lengths
        .into_iter()
        .map(|len| (len, words.iter().copied().filter(|w| w.len() == len).collect()))
        .collect()
}
