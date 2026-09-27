use std::collections::HashSet;

pub fn find_all_concatenated_words<'a>(words: &[&'a str]) -> Vec<&'a str> {
    let set: HashSet<&str> = words.iter().copied().filter(|w| !w.is_empty()).collect();
    words
        .iter()
        .copied()
        .filter(|w| {
            let n = w.len();
            let mut ok = vec![false; n + 1];
            ok[0] = true;
            for i in 1..=n {
                ok[i] = (0..i).any(|j| ok[j] && set.contains(&w[j..i]));
            }
            n > 0 && ok[n]
        })
        .collect()
}
