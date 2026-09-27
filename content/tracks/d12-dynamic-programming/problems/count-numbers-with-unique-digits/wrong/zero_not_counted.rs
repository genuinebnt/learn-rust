pub fn count_numbers_with_unique_digits(n: u32) -> u64 {
    let mut total = 0;
    let mut of_length = 9u64;
    for k in 1..=n.min(10) as u64 {
        if k > 1 {
            of_length *= 11 - k;
        }
        total += of_length;
    }
    total.max(1)
}
