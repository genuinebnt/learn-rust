pub fn group_anagrams(words: &[&str]) -> Vec<Vec<String>> {
    let key = |w: &str| {
        let mut k = w.as_bytes().to_vec();
        k.sort_unstable();
        k
    };
    let mut groups: Vec<(Vec<u8>, Vec<String>)> = Vec::new();
    for &w in words {
        let k = key(w);
        match groups.iter_mut().find(|(g, _)| *g == k) {
            Some((_, g)) => g.push(w.to_string()),
            None => groups.push((k, vec![w.to_string()])),
        }
    }
    let mut out: Vec<Vec<String>> = groups.into_iter().map(|(_, g)| g).collect();
    for g in &mut out {
        g.sort();
    }
    out.sort();
    out
}
