use std::collections::{HashSet, VecDeque};

pub fn ladder_length(begin: &str, end: &str, words: &[&str]) -> usize {
    let mut unseen: HashSet<&[u8]> = words.iter().map(|w| w.as_bytes()).collect();
    if !unseen.contains(end.as_bytes()) {
        return 0;
    }
    unseen.remove(begin.as_bytes());
    let mut queue = VecDeque::from([(begin.as_bytes().to_vec(), 0)]);
    while let Some((mut w, steps)) = queue.pop_front() {
        if w == end.as_bytes() {
            return steps;
        }
        for i in 0..w.len() {
            let original = w[i];
            for b in b'a'..=b'z' {
                w[i] = b;
                if b != original && unseen.remove(w.as_slice()) {
                    queue.push_back((w.to_vec(), steps + 1));
                }
            }
            w[i] = original;
        }
    }
    0
}
