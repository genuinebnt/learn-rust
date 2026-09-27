use std::collections::HashMap;

pub fn least_interval(tasks: &[char], n: usize) -> usize {
    schedule(tasks, n).len()
}

pub fn schedule(tasks: &[char], n: usize) -> Vec<Option<char>> {
    let mut counts: HashMap<char, usize> = HashMap::new();
    for &c in tasks {
        *counts.entry(c).or_insert(0) += 1;
    }
    // (runs left, first slot it may run in, id)
    let mut state: Vec<(usize, usize, char)> = counts.into_iter().map(|(c, k)| (k, 0, c)).collect();
    let mut remaining = tasks.len();
    let mut out = Vec::new();
    while remaining > 0 {
        let t = out.len();
        let pick = (0..state.len()).filter(|&i| state[i].0 > 0 && state[i].1 <= t).max_by_key(|&i| state[i].0);
        match pick {
            Some(i) => {
                state[i].0 -= 1;
                state[i].1 = t + n + 1;
                remaining -= 1;
                out.push(Some(state[i].2));
            }
            None => out.push(None),
        }
    }
    out
}
