pub fn count_substrings(s: &str) -> usize {
    let chars: Vec<char> = s.chars().collect();
    let mut count = 0;
    for i in 0..chars.len() {
        let (mut l, mut r) = (i, i);
        while r < chars.len() && chars[l] == chars[r] {
            count += 1;
            if l == 0 {
                break;
            }
            l -= 1;
            r += 1;
        }
    }
    count
}
