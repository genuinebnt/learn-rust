pub fn total_n_queens(n: usize) -> usize {
    fn go(n: usize, queens: &mut Vec<usize>) -> usize {
        let row = queens.len();
        if row == n {
            return 1;
        }
        let mut total = 0;
        for c in 0..n {
            if queens.iter().enumerate().all(|(r, &q)| q != c && q.abs_diff(c) != row - r) {
                queens.push(c);
                total += go(n, queens);
                queens.pop();
            }
        }
        total
    }
    go(n, &mut Vec::new())
}
