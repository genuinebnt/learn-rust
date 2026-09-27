use std::collections::HashMap;

pub fn reorganize(s: &str) -> Option<String> {
    let mut counts: HashMap<char, usize> = HashMap::new();
    for c in s.chars() {
        *counts.entry(c).or_insert(0) += 1;
    }
    let mut left: Vec<(char, usize)> = counts.into_iter().collect();
    let mut out = String::new();
    let mut last = None;
    for _ in 0..s.chars().count() {
        let i = (0..left.len()).filter(|&i| left[i].1 > 0 && Some(left[i].0) != last).max_by_key(|&i| left[i].1)?;
        left[i].1 -= 1;
        out.push(left[i].0);
        last = Some(left[i].0);
    }
    Some(out)
}
