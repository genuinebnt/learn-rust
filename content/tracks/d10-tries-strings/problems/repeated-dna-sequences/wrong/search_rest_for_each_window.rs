pub fn find_repeated_dna_sequences(s: &str, k: usize) -> Vec<&str> {
    let mut out: Vec<&str> = Vec::new();
    for i in 0..(s.len() + 1).saturating_sub(k) {
        let w = &s[i..i + k];
        if !s[..i + k - 1].contains(w) && s[i + 1..].contains(w) {
            out.push(w);
        }
    }
    out
}
