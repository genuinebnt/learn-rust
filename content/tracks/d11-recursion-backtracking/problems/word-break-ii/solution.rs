use std::collections::HashSet;

pub fn word_break(s: &str, word_dict: &[&str]) -> Vec<String> {
    let words: HashSet<&str> = word_dict.iter().copied().collect();
    let longest = words.iter().map(|w| w.len()).max().unwrap_or(0);
    let n = s.len();
    // finishes[i]: s[i..] splits into words. Built from the back, like Word break I.
    let mut finishes = vec![false; n + 1];
    finishes[n] = true;
    for i in (0..n).rev() {
        finishes[i] = (i + 1..=n.min(i + longest)).any(|j| finishes[j] && words.contains(&s[i..j]));
    }

    // Only steps to positions that can still finish, so every branch ends in a sentence.
    fn build<'a>(s: &'a str, i: usize, words: &HashSet<&str>, longest: usize, finishes: &[bool], path: &mut Vec<&'a str>, out: &mut Vec<String>) {
        if i == s.len() {
            out.push(path.join(" "));
            return;
        }
        for j in i + 1..=s.len().min(i + longest) {
            if finishes[j] && words.contains(&s[i..j]) {
                path.push(&s[i..j]);
                build(s, j, words, longest, finishes, path, out);
                path.pop();
            }
        }
    }
    let mut out = Vec::new();
    if finishes[0] {
        build(s, 0, &words, longest, &finishes, &mut Vec::new(), &mut out);
    }
    out
}
