pub fn merge_k_sorted(arrays: &[Vec<i32>]) -> Vec<i32> {
    let mut pos = vec![0; arrays.len()];
    let mut out = Vec::new();
    loop {
        let best = (0..arrays.len()).filter(|&a| pos[a] < arrays[a].len()).min_by_key(|&a| arrays[a][pos[a]]);
        let Some(a) = best else { break };
        out.push(arrays[a][pos[a]]);
        pos[a] += 1;
    }
    out
}
