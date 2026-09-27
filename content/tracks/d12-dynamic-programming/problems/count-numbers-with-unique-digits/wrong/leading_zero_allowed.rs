pub fn count_numbers_with_unique_digits(n: u32) -> u64 {
    let mut total = 1;
    let mut of_length = 1u64;
    for k in 1..=n.min(10) as u64 {
        of_length *= 11 - k;
        total += of_length;
    }
    total
}
