use std::collections::HashMap;

pub fn find_repeated_dna_sequences(s: &str, k: usize) -> Vec<&str> {
    let mut count: HashMap<&str, usize> = HashMap::new();
    let mut out = Vec::new();
    for i in 0..(s.len() + 1).saturating_sub(k) {
        let w = &s[i..i + k];
        let c = count.entry(w).or_insert(0);
        *c += 1;
        if *c == 2 {
            out.push(w);
        }
    }
    out
}
