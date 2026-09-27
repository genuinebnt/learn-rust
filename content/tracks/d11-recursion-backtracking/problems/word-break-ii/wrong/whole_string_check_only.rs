use std::collections::HashSet;

pub fn word_break(s: &str, word_dict: &[&str]) -> Vec<String> {
    fn build<'a>(s: &'a str, i: usize, words: &HashSet<&str>, path: &mut Vec<&'a str>, out: &mut Vec<String>) {
        if i == s.len() {
            out.push(path.join(" "));
            return;
        }
        for j in i + 1..=s.len() {
            if words.contains(&s[i..j]) {
                path.push(&s[i..j]);
                build(s, j, words, path, out);
                path.pop();
            }
        }
    }
    let words: HashSet<&str> = word_dict.iter().copied().collect();
    let n = s.len();
    // Word break I: can s be split at all?
    let mut splits = vec![false; n + 1];
    splits[0] = true;
    for j in 1..=n {
        splits[j] = (0..j).any(|i| splits[i] && words.contains(&s[i..j]));
    }
    let mut out = Vec::new();
    if splits[n] {
        build(s, 0, &words, &mut Vec::new(), &mut out);
    }
    out
}
