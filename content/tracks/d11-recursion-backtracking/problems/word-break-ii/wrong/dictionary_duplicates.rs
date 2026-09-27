pub fn word_break(s: &str, word_dict: &[&str]) -> Vec<String> {
    let n = s.len();
    let mut finishes = vec![false; n + 1];
    finishes[n] = true;
    for i in (0..n).rev() {
        finishes[i] = word_dict.iter().any(|w| s[i..].starts_with(w) && finishes[i + w.len()]);
    }
    fn build<'a>(s: &'a str, i: usize, dict: &[&'a str], finishes: &[bool], path: &mut Vec<&'a str>, out: &mut Vec<String>) {
        if i == s.len() {
            out.push(path.join(" "));
            return;
        }
        for &w in dict {
            if s[i..].starts_with(w) && finishes[i + w.len()] {
                path.push(w);
                build(s, i + w.len(), dict, finishes, path, out);
                path.pop();
            }
        }
    }
    let mut out = Vec::new();
    if finishes[0] {
        build(s, 0, word_dict, &finishes, &mut Vec::new(), &mut out);
    }
    out
}
