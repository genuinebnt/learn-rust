fn counts(tasks: &[char]) -> [usize; 26] {
    let mut counts = [0; 26];
    for &c in tasks {
        counts[(c as u8 - b'A') as usize] += 1;
    }
    counts
}

pub fn least_interval(tasks: &[char], n: usize) -> usize {
    let counts = counts(tasks);
    let most = *counts.iter().max().unwrap();
    if most == 0 {
        return 0;
    }
    let tied = counts.iter().filter(|&&c| c == most).count();
    tasks.len().max((most - 1) * (n + 1) + tied)
}

pub fn schedule(tasks: &[char], n: usize) -> Vec<Option<char>> {
    let mut left = counts(tasks);
    let mut next_ok = [0usize; 26];
    let mut out = Vec::new();
    let mut remaining = tasks.len();
    while remaining > 0 {
        let t = out.len();
        let pick = (0..26).filter(|&i| left[i] > 0 && next_ok[i] <= t).max_by_key(|&i| left[i]);
        match pick {
            Some(i) => {
                left[i] -= 1;
                remaining -= 1;
                next_ok[i] = t + n + 1;
                out.push(Some((b'A' + i as u8) as char));
            }
            None => out.push(None),
        }
    }
    out
}
