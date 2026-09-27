pub fn number_ways(hats: &[Vec<u8>]) -> u64 {
    const MOD: u64 = 1_000_000_007;
    let n = hats.len();
    // likes[h] = the people who would wear hat h, as a bitmask.
    let mut likes = [0usize; 41];
    for (person, list) in hats.iter().enumerate() {
        for &h in list {
            likes[h as usize] |= 1 << person;
        }
    }
    // ways[mask] = ways to dress exactly the people in mask using the hats handled so far.
    let mut ways = vec![0u64; 1 << n];
    ways[0] = 1;
    for h in 1..=40 {
        // Downwards, so ways[mask ^ p] still excludes hat h: it goes to one person at most.
        for mask in (1..1usize << n).rev() {
            let mut wearers = likes[h] & mask;
            while wearers != 0 {
                let p = wearers & wearers.wrapping_neg();
                ways[mask] = (ways[mask] + ways[mask ^ p]) % MOD;
                wearers ^= p;
            }
        }
    }
    ways[(1 << n) - 1]
}
