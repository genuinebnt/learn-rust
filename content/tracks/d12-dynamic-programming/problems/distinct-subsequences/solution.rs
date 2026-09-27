pub fn num_distinct(s: &str, t: &str) -> u64 {
    let t = t.as_bytes();
    // ways[j] = ways to spell t[..j] with the part of s seen so far.
    let mut ways = vec![0u64; t.len() + 1];
    ways[0] = 1;
    for &c in s.as_bytes() {
        // Backwards, so this c extends only spellings that didn't use it already.
        for j in (1..=t.len()).rev() {
            if t[j - 1] == c {
                // Partial counts may wrap; the final answer is exact because it fits.
                ways[j] = ways[j].wrapping_add(ways[j - 1]);
            }
        }
    }
    ways[t.len()]
}
