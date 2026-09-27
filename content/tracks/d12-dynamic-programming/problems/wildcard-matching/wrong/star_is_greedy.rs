pub fn is_match(s: &str, p: &str) -> bool {
    // Lets each '*' swallow characters until the next pattern character shows up, never backing off.
    let s: Vec<char> = s.chars().collect();
    let p: Vec<char> = p.chars().collect();
    let (mut i, mut j) = (0, 0);
    while j < p.len() {
        match p[j] {
            '*' => {
                j += 1;
                match p.get(j) {
                    None => return true,
                    Some('?') | Some('*') => {}
                    Some(&q) => {
                        while i < s.len() && s[i] != q {
                            i += 1;
                        }
                    }
                }
            }
            q => {
                if i == s.len() || (q != '?' && q != s[i]) {
                    return false;
                }
                i += 1;
                j += 1;
            }
        }
    }
    i == s.len()
}
