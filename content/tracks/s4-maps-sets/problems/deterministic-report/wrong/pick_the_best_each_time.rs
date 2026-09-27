use std::collections::HashMap;

pub fn report(scores: &HashMap<String, u32>) -> Vec<String> {
    let mut left: Vec<(&String, &u32)> = scores.iter().collect();
    let mut out = Vec::new();
    while !left.is_empty() {
        let mut best = 0;
        for i in 1..left.len() {
            let (a, b) = (left[i], left[best]);
            if a.1 > b.1 || (a.1 == b.1 && a.0 < b.0) {
                best = i;
            }
        }
        let (name, score) = left.remove(best);
        out.push(format!("{name}: {score}"));
    }
    out
}
