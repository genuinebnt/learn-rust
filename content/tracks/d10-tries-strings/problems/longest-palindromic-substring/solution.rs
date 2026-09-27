/// Grows the palindrome `chars[l..r]` outwards while both ends match.
fn expand(chars: &[char], mut l: usize, mut r: usize) -> (usize, usize) {
    while l > 0 && r < chars.len() && chars[l - 1] == chars[r] {
        l -= 1;
        r += 1;
    }
    (l, r)
}

pub fn longest_palindrome(s: &str) -> &str {
    let chars: Vec<char> = s.chars().collect();
    // Byte offset of every character, plus the end, so a char range maps back to a slice of `s`.
    let offsets: Vec<usize> = s.char_indices().map(|(i, _)| i).chain([s.len()]).collect();
    let (mut lo, mut hi) = (0, 0);
    for i in 0..chars.len() {
        // Odd length: centred on char i. Even length: centred on the gap before char i.
        for (l, r) in [expand(&chars, i, i + 1), expand(&chars, i, i)] {
            // Strictly longer only, so the earliest start wins a tie.
            if r - l > hi - lo {
                (lo, hi) = (l, r);
            }
        }
    }
    &s[offsets[lo]..offsets[hi]]
}
