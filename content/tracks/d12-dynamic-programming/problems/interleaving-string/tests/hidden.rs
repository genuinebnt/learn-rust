use solution::*;

#[test]
fn too_short() {
    check!(r#"s1 = "abc", s2 = "", s3 = "ab""#, is_interleave("abc", "", "ab"), false);
}

#[test]
fn empty_s3() {
    check!(r#"s1 = "a", s2 = "", s3 = """#, is_interleave("a", "", ""), false);
}

#[test]
fn order_kept() {
    check!(r#"s1 = "ab", s2 = "", s3 = "ba""#, is_interleave("ab", "", "ba"), false);
}

#[test]
fn symmetric() {
    check!(r#"s1 = "ab", s2 = "ba", s3 = "abba""#, is_interleave("ab", "ba", "abba"), true);
}

#[test]
fn greedy_trap() {
    check!(r#"s1 = "aa", s2 = "ab", s3 = "abaa""#, is_interleave("aa", "ab", "abaa"), true);
}

#[test]
fn greedy_trap_longer() {
    check!(r#"s1 = "abc", s2 = "abd", s3 = "abdabc""#, is_interleave("abc", "abd", "abdabc"), true);
}

#[test]
fn shared_letters() {
    check!(r#"s1 = "db", s2 = "b", s3 = "dbb""#, is_interleave("db", "b", "dbb"), true);
}

#[test]
fn same_letters_wrong_count() {
    check!(r#"s1 = "aa", s2 = "a", s3 = "aab""#, is_interleave("aa", "a", "aab"), false);
}

#[test]
fn random_vs_brute_force() {
    fn can(a: &[u8], b: &[u8], c: &[u8]) -> bool {
        match c {
            [] => a.is_empty() && b.is_empty(),
            [x, rest @ ..] => (a.first() == Some(x) && can(&a[1..], b, rest)) || (b.first() == Some(x) && can(a, &b[1..], rest)),
        }
    }
    let mut rng = anneal_prelude::Rng::new(1228);
    for _ in 0..400 {
        let (l1, l2) = (rng.below(5), rng.below(5));
        let s1 = rng.string(l1, "ab");
        let s2 = rng.string(l2, "ab");
        let l3 = if rng.below(8) == 0 { rng.below(9) } else { l1 + l2 };
        let s3 = rng.string(l3, "ab");
        check!(format!("s1 = {s1:?}, s2 = {s2:?}, s3 = {s3:?}"), is_interleave(&s1, &s2, &s3), can(s1.as_bytes(), s2.as_bytes(), s3.as_bytes()));
    }
}

#[test]
fn scale_all_a_then_b() {
    // Every split of the a's matches until the final b: plain recursion tries them all.
    let s1 = "a".repeat(1000);
    let s2 = "a".repeat(1000);
    let s3 = format!("{}b", "a".repeat(1999));
    check!("s1 = s2 = 1000 a's, s3 = 1999 a's then b", is_interleave(&s1, &s2, &s3), false);
}

#[test]
fn scale_real_interleave() {
    let s1: Vec<u8> = (0..1000usize).map(|i| b'a' + (i * 7 % 3) as u8).collect();
    let s2: Vec<u8> = (0..1000usize).map(|i| b'a' + ((i * 5 + 1) % 3) as u8).collect();
    let mut s3 = Vec::new();
    let (mut i, mut j, mut k) = (0, 0, 0usize);
    while i < 1000 || j < 1000 {
        if j >= 1000 || (i < 1000 && k * 7919 % 3 != 0) {
            s3.push(s1[i]);
            i += 1;
        } else {
            s3.push(s2[j]);
            j += 1;
        }
        k += 1;
    }
    let (s1, s2, s3) = (String::from_utf8(s1).unwrap(), String::from_utf8(s2).unwrap(), String::from_utf8(s3).unwrap());
    check!("s1, s2 = 1000 letters of a/b/c, s3 = one interleaving of them", is_interleave(&s1, &s2, &s3), true);
}
