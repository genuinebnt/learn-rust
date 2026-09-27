pub fn count_substrings(s: &str) -> usize {
    let chars: Vec<char> = s.chars().collect();
    let n = chars.len();
    let mut count = 0;
    for i in 0..n {
        // Odd palindromes centred on char i, then even ones centred on the gap after it.
        for (mut l, mut r) in [(i, i), (i, i + 1)] {
            while r < n && chars[l] == chars[r] {
                count += 1;
                if l == 0 {
                    break;
                }
                l -= 1;
                r += 1;
            }
        }
    }
    count
}
