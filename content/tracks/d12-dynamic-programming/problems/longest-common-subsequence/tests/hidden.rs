use solution::*;

#[test]
fn both_empty() {
    check!(r#"a = "", b = """#, longest_common_subsequence("", ""), 0);
}

#[test]
fn second_empty() {
    check!(r#"a = "abc", b = """#, longest_common_subsequence("abc", ""), 0);
}

#[test]
fn single_match() {
    check!(r#"a = "a", b = "a""#, longest_common_subsequence("a", "a"), 1);
}

#[test]
fn repeats() {
    check!(r#"a = "aaaa", b = "aa""#, longest_common_subsequence("aaaa", "aa"), 2);
}

#[test]
fn first_match_is_wrong() {
    check!(r#"a = "xab", b = "abx""#, longest_common_subsequence("xab", "abx"), 2);
}

#[test]
fn short_second() {
    check!(r#"a = "bl", b = "yby""#, longest_common_subsequence("bl", "yby"), 1);
}

#[test]
fn leetcode_mixed() {
    check!(r#"a = "ezupkr", b = "ubmrapg""#, longest_common_subsequence("ezupkr", "ubmrapg"), 2);
}

#[test]
fn leetcode_mixed_longer() {
    check!(r#"a = "oxcpqrsvwf", b = "shmtulqrypy""#, longest_common_subsequence("oxcpqrsvwf", "shmtulqrypy"), 2);
}

#[test]
fn random_vs_brute_force() {
    fn is_subsequence(small: &[u8], big: &[u8]) -> bool {
        let mut it = big.iter();
        small.iter().all(|c| it.any(|d| d == c))
    }
    let mut rng = anneal_prelude::Rng::new(1224);
    for _ in 0..300 {
        let (la, lb) = (rng.below(9), rng.below(9));
        let a = rng.string(la, "abc");
        let b = rng.string(lb, "abc");
        let ab = a.as_bytes();
        let mut want = 0;
        for mask in 0u32..(1 << la) {
            let picked: Vec<u8> = (0..la).filter(|&i| mask >> i & 1 == 1).map(|i| ab[i]).collect();
            if is_subsequence(&picked, b.as_bytes()) {
                want = want.max(picked.len());
            }
        }
        check!(format!("a = {a:?}, b = {b:?}"), longest_common_subsequence(&a, &b), want);
    }
}

#[test]
fn scale_2000() {
    let a: String = (0..2000u64).map(|i| (b'a' + (i * 7919 % 26) as u8) as char).collect();
    let b: String = (0..2000u64).map(|i| (b'a' + ((i * 104_729 + 13) % 26) as u8) as char).collect();
    check!("a[i] = 'a' + (7919·i) % 26, b[i] = 'a' + (104729·i + 13) % 26, 2000 each", longest_common_subsequence(&a, &b), 615);
}
