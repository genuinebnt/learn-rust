pub fn count_numbers_with_unique_digits(n: u32) -> u64 {
    let unique = |mut x: u64| {
        let mut seen = [false; 10];
        loop {
            let d = (x % 10) as usize;
            if seen[d] {
                return false;
            }
            seen[d] = true;
            x /= 10;
            if x == 0 {
                return true;
            }
        }
    };
    (0..10u64.pow(n.min(10))).filter(|&x| unique(x)).count() as u64
}
