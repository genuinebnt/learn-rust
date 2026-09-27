use std::collections::HashSet;

pub fn count_substrings(s: &str) -> usize {
    let chars: Vec<char> = s.chars().collect();
    let mut seen: HashSet<&[char]> = HashSet::new();
    for i in 0..chars.len() {
        for (mut l, mut r) in [(i, i), (i, i + 1)] {
            while r < chars.len() && chars[l] == chars[r] {
                seen.insert(&chars[l..=r]);
                if l == 0 {
                    break;
                }
                l -= 1;
                r += 1;
            }
        }
    }
    seen.len()
}
