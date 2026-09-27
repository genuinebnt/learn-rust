use std::collections::HashMap;

fn is_palindrome(b: &[u8]) -> bool {
    b.iter().eq(b.iter().rev())
}

pub fn palindrome_pairs(words: &[&str]) -> Vec<(usize, usize)> {
    let reversed: HashMap<Vec<u8>, usize> = words.iter().enumerate().map(|(i, w)| (w.bytes().rev().collect(), i)).collect();
    let mut out = Vec::new();
    for (i, w) in words.iter().enumerate() {
        let b = w.as_bytes();
        // Proper splits only: both sides non-empty, plus the plain reverse.
        for cut in 1..b.len() {
            let (left, right) = b.split_at(cut);
            if is_palindrome(right) {
                if let Some(&j) = reversed.get(left) {
                    out.push((i, j));
                }
            }
            if is_palindrome(left) {
                if let Some(&j) = reversed.get(right) {
                    out.push((j, i));
                }
            }
        }
        if let Some(&j) = reversed.get(b) {
            if j != i {
                out.push((i, j));
            }
        }
    }
    out.sort_unstable();
    out
}
