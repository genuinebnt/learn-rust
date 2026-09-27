pub fn solve_n_queens(n: usize) -> Vec<Vec<String>> {
    fn go(n: usize, queens: &mut Vec<usize>, taken: &mut Vec<bool>, out: &mut Vec<Vec<String>>) {
        if queens.len() == n {
            if (0..n).all(|i| (i + 1..n).all(|j| queens[i].abs_diff(queens[j]) != j - i)) {
                out.push(queens.iter().map(|&q| (0..n).map(|c| if c == q { 'Q' } else { '.' }).collect()).collect());
            }
            return;
        }
        for c in 0..n {
            if !taken[c] {
                taken[c] = true;
                queens.push(c);
                go(n, queens, taken, out);
                queens.pop();
                taken[c] = false;
            }
        }
    }
    let mut out = Vec::new();
    go(n, &mut Vec::new(), &mut vec![false; n], &mut out);
    out
}
