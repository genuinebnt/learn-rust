fn count(hats: &[Vec<u8>], used: &mut [bool; 41]) -> u64 {
    let Some((first, rest)) = hats.split_first() else { return 1 };
    let mut total = 0;
    for &h in first {
        if !used[h as usize] {
            used[h as usize] = true;
            total = (total + count(rest, used)) % 1_000_000_007;
            used[h as usize] = false;
        }
    }
    total
}

pub fn number_ways(hats: &[Vec<u8>]) -> u64 {
    count(hats, &mut [false; 41])
}
