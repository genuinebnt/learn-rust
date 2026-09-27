pub fn num_squares(n: u32) -> u32 {
    if n == 0 {
        return 0;
    }
    (1..).take_while(|j| j * j <= n).map(|j| num_squares(n - j * j) + 1).min().unwrap()
}
