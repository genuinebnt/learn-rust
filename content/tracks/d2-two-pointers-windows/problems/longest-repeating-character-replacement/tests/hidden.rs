use solution::*;

#[test]
fn zero_k() {
    check!(r#"s = "ABBB", k = 0"#, character_replacement("ABBB", 0), 3);
}

#[test]
fn empty() {
    check!(r#"s = "", k = 3"#, character_replacement("", 3), 0);
}

#[test]
fn single() {
    check!(r#"s = "Q", k = 0"#, character_replacement("Q", 0), 1);
}

#[test]
fn k_past_length() {
    check!(r#"s = "AB", k = 5"#, character_replacement("AB", 5), 2);
}

#[test]
fn all_same() {
    check!(r#"s = "ZZZZ", k = 0"#, character_replacement("ZZZZ", 0), 4);
}

#[test]
fn zero_k_alternating() {
    check!(r#"s = "ABABAB", k = 0"#, character_replacement("ABABAB", 0), 1);
}

#[test]
fn best_run_late() {
    check!(r#"s = "ABCDEEEEF", k = 1"#, character_replacement("ABCDEEEEF", 1), 5);
}

#[test]
fn fill_a_gap() {
    check!(r#"s = "AAABAAACAA", k = 2"#, character_replacement("AAABAAACAA", 2), 10);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(213);
    for _ in 0..300 {
        let n = rng.below(14);
        let s = rng.string(n, "ABC");
        let k = rng.below(4);
        let b = s.as_bytes();
        let mut want = 0;
        for i in 0..n {
            for j in i..n {
                let w = &b[i..=j];
                let most = (b'A'..=b'C').map(|c| w.iter().filter(|&&x| x == c).count()).max().unwrap();
                if w.len() - most <= k {
                    want = want.max(w.len());
                }
            }
        }
        check!(format!("s = {s:?}, k = {k}"), character_replacement(&s, k), want);
    }
}

#[test]
fn scale_200k() {
    let s = "AB".repeat(100_000);
    check!("s = \"AB\" × 100000, k = 100000 / 99999", (character_replacement(&s, 100_000), character_replacement(&s, 99_999)), (200_000, 199_999));
}
