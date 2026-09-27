pub fn longest_palindrome_subseq(s: &str) -> usize {
    let mut counts = [0usize; 26];
    for b in s.bytes() {
        counts[(b - b'a') as usize] += 1;
    }
    let pairs: usize = counts.iter().map(|c| c / 2 * 2).sum();
    pairs + counts.iter().any(|c| c % 2 == 1) as usize
}
