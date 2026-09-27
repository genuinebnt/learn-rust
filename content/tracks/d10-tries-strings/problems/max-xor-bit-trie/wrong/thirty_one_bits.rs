pub fn find_maximum_xor(nums: &[u32]) -> u32 {
    let mut trie: Vec<[u32; 2]> = vec![[0, 0]];
    let mut best = 0;
    for (i, &x) in nums.iter().enumerate() {
        if i > 0 {
            let (mut at, mut xor) = (0, 0u32);
            for bit in (0..31).rev() {
                let b = (x >> bit & 1) as usize;
                let other = trie[at][b ^ 1];
                if other != 0 {
                    xor |= 1 << bit;
                    at = other as usize;
                } else {
                    at = trie[at][b] as usize;
                }
            }
            best = best.max(xor);
        }
        let mut at = 0;
        for bit in (0..31).rev() {
            let b = (x >> bit & 1) as usize;
            if trie[at][b] == 0 {
                trie.push([0, 0]);
                trie[at][b] = (trie.len() - 1) as u32;
            }
            at = trie[at][b] as usize;
        }
    }
    best
}
