pub fn get_order(tasks: &[(u32, u32)]) -> Vec<usize> {
    let n = tasks.len();
    let mut done = vec![false; n];
    let mut clock = 0u64;
    let mut out = Vec::new();
    while out.len() < n {
        let pick = (0..n).filter(|&i| !done[i] && tasks[i].0 as u64 <= clock).min_by_key(|&i| (tasks[i].1, i));
        match pick {
            Some(i) => {
                done[i] = true;
                clock += tasks[i].1 as u64;
                out.push(i);
            }
            None => clock = (0..n).filter(|&i| !done[i]).map(|i| tasks[i].0 as u64).min().unwrap(),
        }
    }
    out
}
