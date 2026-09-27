pub fn find_max_form(strs: &[&str], m: usize, n: usize) -> usize {
    let mut best = vec![vec![0usize; n + 1]; m + 1];
    for s in strs {
        let zeros = s.bytes().filter(|&b| b == b'0').count();
        let ones = s.len() - zeros;
        for z in zeros..=m {
            for o in ones..=n {
                best[z][o] = best[z][o].max(best[z - zeros][o - ones] + 1);
            }
        }
    }
    best[m][n]
}
