use std::collections::BTreeSet;

pub fn alien_order(words: &[&str]) -> Option<String> {
    let mut present = [false; 26];
    for w in words {
        for b in w.bytes() {
            present[(b - b'a') as usize] = true;
        }
    }
    let mut before = [[false; 26]; 26];
    let mut indeg = [0u32; 26];
    for pair in words.windows(2) {
        let (a, b) = (pair[0].as_bytes(), pair[1].as_bytes());
        match a.iter().zip(b).find(|(x, y)| x != y) {
            Some((&x, &y)) => {
                let (x, y) = ((x - b'a') as usize, (y - b'a') as usize);
                if !before[x][y] {
                    before[x][y] = true;
                    indeg[y] += 1;
                }
            }
            None if a.len() > b.len() => return None,
            None => {}
        }
    }
    let mut ready: BTreeSet<usize> = (0..26).filter(|&c| present[c] && indeg[c] == 0).collect();
    let mut out = String::new();
    while let Some(c) = ready.pop_first() {
        out.push((b'a' + c as u8) as char);
        for d in 0..26 {
            if before[c][d] {
                indeg[d] -= 1;
                if indeg[d] == 0 {
                    ready.insert(d);
                }
            }
        }
    }
    (out.len() == present.iter().filter(|&&p| p).count()).then_some(out)
}
