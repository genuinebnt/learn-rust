pub fn count_numbers_with_unique_digits(n: u32) -> u64 {
    // 0 on its own, then the numbers of each length k = 1..=n. A k-digit number has 9 choices
    // for its first digit (1-9) and 9, 8, 7, ... for the rest, since each must be new.
    let mut total = 1;
    let mut of_length = 9u64;
    // Past 10 digits some digit must repeat, so longer lengths add nothing.
    for k in 1..=n.min(10) as u64 {
        if k > 1 {
            of_length *= 11 - k;
        }
        total += of_length;
    }
    total
}
