pub fn is_anagram(s: &str, t: &str) -> bool {
    let mut counts = [0i32; 26];
    for (a, b) in s.bytes().zip(t.bytes()) {
        counts[(a - b'a') as usize] += 1;
        counts[(b - b'a') as usize] -= 1;
    }
    counts.iter().all(|&c| c == 0)
}
