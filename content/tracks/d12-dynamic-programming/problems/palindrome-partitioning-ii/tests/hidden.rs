use solution::*;

#[test]
fn empty() {
    check!(r#"s = """#, min_cut(""), 0);
}

#[test]
fn all_different() {
    check!(r#"s = "abcde""#, min_cut("abcde"), 4);
}

#[test]
fn all_same() {
    check!(r#"s = "aaaa""#, min_cut("aaaa"), 0);
}

#[test]
fn two_pieces() {
    check!(r#"s = "cdd""#, min_cut("cdd"), 1);
}

#[test]
fn even_palindromes() {
    check!(r#"s = "abccbc""#, min_cut("abccbc"), 2);
}

#[test]
fn greedy_trap() {
    check!(r#"s = "ababbbabbababa""#, min_cut("ababbbabbababa"), 3);
}

#[test]
fn long_mixed() {
    check!(r#"s = "eegiicgaeadbcfacfhifdbiehbgejcaeggcgbahfcajfhjjdgj""#, min_cut("eegiicgaeadbcfacfhifdbiehbgejcaeggcgbahfcajfhjjdgj"), 42);
}

#[test]
fn longest_all_same() {
    check!(r#"s = "aaa…a" (2000)"#, min_cut(&"a".repeat(2000)), 0);
}

#[test]
fn random_vs_brute_force() {
    fn fewest_pieces(s: &[u8]) -> usize {
        if s.is_empty() {
            return 0;
        }
        (1..=s.len()).filter(|&k| s[..k].iter().eq(s[..k].iter().rev())).map(|k| 1 + fewest_pieces(&s[k..])).min().unwrap()
    }
    let mut rng = anneal_prelude::Rng::new(1243);
    for _ in 0..300 {
        let n = rng.below(11);
        let s = rng.string(n, "ab");
        check!(format!("s = {s:?}"), min_cut(&s), fewest_pieces(s.as_bytes()).saturating_sub(1));
    }
}

#[test]
fn scale_2000() {
    let s: String = (0..2000u64).map(|i| (b'a' + (i * i / 7 % 3) as u8) as char).collect();
    check!("s[i] = 'a' + (i² / 7) % 3, 2000 characters", min_cut(&s), 3);
}

#[test]
fn scale_all_a_then_b() {
    // Every substring of the a's is a palindrome: checking each one from scratch is O(n³).
    let s = format!("{}b", "a".repeat(1999));
    check!("s = 1999 a's then b", min_cut(&s), 1);
}
