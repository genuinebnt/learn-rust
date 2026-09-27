pub fn number_ways(hats: &[Vec<u8>]) -> u64 {
    let n = hats.len();
    let mut likes = [0usize; 41];
    for (person, list) in hats.iter().enumerate() {
        for &h in list {
            likes[h as usize] |= 1 << person;
        }
    }
    let mut ways = vec![0u64; 1 << n];
    ways[0] = 1;
    for h in 1..=40 {
        for mask in (1..1usize << n).rev() {
            let mut wearers = likes[h] & mask;
            while wearers != 0 {
                let p = wearers & wearers.wrapping_neg();
                ways[mask] += ways[mask ^ p];
                wearers ^= p;
            }
        }
    }
    ways[(1 << n) - 1]
}
