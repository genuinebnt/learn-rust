pub fn longest_palindrome(s: &str) -> &str {
    let chars: Vec<char> = s.chars().collect();
    let offsets: Vec<usize> = s.char_indices().map(|(i, _)| i).chain([s.len()]).collect();
    let (mut lo, mut hi) = (0, 0);
    for i in 0..chars.len() {
        for (mut l, mut r) in [(i, i + 1), (i, i)] {
            while l > 0 && r < chars.len() && chars[l - 1] == chars[r] {
                l -= 1;
                r += 1;
            }
            if r - l >= hi - lo {
                (lo, hi) = (l, r);
            }
        }
    }
    &s[offsets[lo]..offsets[hi]]
}
