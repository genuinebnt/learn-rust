pub fn num_squares(n: u32) -> u32 {
    let (mut left, mut used) = (n, 0);
    while left > 0 {
        let mut r = 1;
        while (r + 1) * (r + 1) <= left {
            r += 1;
        }
        left -= r * r;
        used += 1;
    }
    used
}
