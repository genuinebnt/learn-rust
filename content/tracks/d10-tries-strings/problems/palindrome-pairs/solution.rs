use std::collections::HashMap;

fn is_palindrome(b: &[u8]) -> bool {
    b.iter().eq(b.iter().rev())
}

pub fn palindrome_pairs(words: &[&str]) -> Vec<(usize, usize)> {
    // Each word reversed -> its index.
    let reversed: HashMap<Vec<u8>, usize> = words.iter().enumerate().map(|(i, w)| (w.bytes().rev().collect(), i)).collect();
    let mut out = Vec::new();
    for (i, w) in words.iter().enumerate() {
        let b = w.as_bytes();
        for cut in 0..=b.len() {
            let (left, right) = b.split_at(cut);
            // w + partner: the partner is `left` reversed, and `right` is the palindrome in the middle.
            if is_palindrome(right) {
                if let Some(&j) = reversed.get(left) {
                    if j != i {
                        out.push((i, j));
                    }
                }
            }
            // partner + w: the partner is `right` reversed. cut = 0 would repeat the cut = len case of the partner.
            if cut > 0 && is_palindrome(left) {
                if let Some(&j) = reversed.get(right) {
                    if j != i {
                        out.push((j, i));
                    }
                }
            }
        }
    }
    out.sort_unstable();
    out
}
