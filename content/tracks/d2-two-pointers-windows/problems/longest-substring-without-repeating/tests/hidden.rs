use solution::*;

#[test]
fn empty() {
    check!(r#"s = """#, length_of_longest_substring(""), 0);
}

#[test]
fn stale_repeat() {
    check!(r#"s = "abba""#, length_of_longest_substring("abba"), 2);
}

#[test]
fn spaces() {
    check!(r#"s = " a b""#, length_of_longest_substring(" a b"), 3);
}

#[test]
fn single() {
    check!(r#"s = "x""#, length_of_longest_substring("x"), 1);
}

#[test]
fn dvdf() {
    check!(r#"s = "dvdf""#, length_of_longest_substring("dvdf"), 3);
}

#[test]
fn all_distinct() {
    check!(r#"s = "abcdefghijklmnopqrstuvwxyz""#, length_of_longest_substring("abcdefghijklmnopqrstuvwxyz"), 26);
}

#[test]
fn case_sensitive() {
    check!(r#"s = "aAbB""#, length_of_longest_substring("aAbB"), 4);
}

#[test]
fn digits_and_symbols() {
    check!(r#"s = "12!1@#""#, length_of_longest_substring("12!1@#"), 5);
}

#[test]
fn every_ascii_byte() {
    check!(r#"s = every ASCII byte 0..128, twice"#, { let s: String = (0u8..128).chain(0u8..128).map(char::from).collect(); length_of_longest_substring(&s) }, 128);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(212);
    for _ in 0..300 {
        let n = rng.below(14);
        let s = rng.string(n, "abcd ");
        let b = s.as_bytes();
        let mut want = 0;
        for i in 0..n {
            for j in i..n {
                let w = &b[i..=j];
                if (0..w.len()).all(|x| !w[x + 1..].contains(&w[x])) {
                    want = want.max(w.len());
                }
            }
        }
        check!(format!("s = {s:?}"), length_of_longest_substring(&s), want);
    }
}

#[test]
fn scale_200k() {
    let printable: String = (0x20u8..0x7f).map(char::from).collect();
    let s = "a".repeat(200_000 - printable.len()) + &printable;
    check!("s = \"a\" × 199905 followed by the 95 printable ASCII characters", length_of_longest_substring(&s), 95);
}
