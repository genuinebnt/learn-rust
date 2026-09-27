pub fn alien_order(words: &[&str]) -> Option<String> {
    let mut present = [false; 26];
    let mut before = [[false; 26]; 26];
    for (i, w) in words.iter().enumerate() {
        for b in w.bytes() {
            present[(b - b'a') as usize] = true;
        }
        for v in &words[i + 1..] {
            let (a, b) = (w.as_bytes(), v.as_bytes());
            match a.iter().zip(b).find(|(x, y)| x != y) {
                Some((&x, &y)) => before[(x - b'a') as usize][(y - b'a') as usize] = true,
                None if a.len() > b.len() => return None,
                None => {}
            }
        }
    }
    let mut out = String::new();
    let mut done = [false; 26];
    while let Some(c) = (0..26).find(|&c| present[c] && !done[c] && (0..26).all(|p| !before[p][c] || done[p])) {
        done[c] = true;
        out.push((b'a' + c as u8) as char);
    }
    (out.len() == present.iter().filter(|&&p| p).count()).then_some(out)
}
