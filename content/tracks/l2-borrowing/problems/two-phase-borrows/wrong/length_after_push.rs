pub fn push_lengths(v: &mut Vec<usize>, n: usize) {
    for _ in 0..n {
        v.push(0);
        let last = v.len() - 1;
        v[last] = v.len();
    }
}
