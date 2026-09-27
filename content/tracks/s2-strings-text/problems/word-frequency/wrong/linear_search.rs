use std::io::{self, BufRead};

pub fn word_frequencies<R: BufRead>(input: R) -> io::Result<Vec<(String, u32)>> {
    let mut pairs: Vec<(String, u32)> = Vec::new();
    for line in input.lines() {
        let line = line?;
        for raw in line.split_whitespace() {
            let word = raw.trim_matches(|c: char| !c.is_alphanumeric()).to_lowercase();
            if word.is_empty() {
                continue;
            }
            match pairs.iter().position(|(w, _)| *w == word) {
                Some(i) => pairs[i].1 += 1,
                None => pairs.push((word, 1)),
            }
        }
    }
    pairs.sort_by(|a, b| b.1.cmp(&a.1).then_with(|| a.0.cmp(&b.0)));
    Ok(pairs)
}
