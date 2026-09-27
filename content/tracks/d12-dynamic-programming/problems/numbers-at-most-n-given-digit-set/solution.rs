pub fn at_most_n_given_digit_set(digits: &[u8], n: u64) -> u64 {
    let s: Vec<u8> = n.to_string().bytes().map(|b| b - b'0').collect();
    let d = digits.len() as u64;
    let len = s.len();
    // Every number shorter than n: d choices in each of its k positions.
    let mut total: u64 = (1..len as u32).map(|k| d.pow(k)).sum();
    // Same length as n: match n's prefix, then put a smaller digit at position i;
    // the positions after it are free.
    for (i, &c) in s.iter().enumerate() {
        let smaller = digits.iter().filter(|&&x| x < c).count() as u64;
        total += smaller * d.pow((len - i - 1) as u32);
        if !digits.contains(&c) {
            // The prefix can't continue matching n.
            return total;
        }
    }
    // Every digit of n is available, so n itself counts too.
    total + 1
}
