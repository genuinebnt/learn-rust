use solution::*;

#[test]
fn empty() {
    check!(r#"s = """#, longest_palindrome_subseq(""), 0);
}

#[test]
fn pair() {
    check!(r#"s = "aa""#, longest_palindrome_subseq("aa"), 2);
}

#[test]
fn different_pair() {
    check!(r#"s = "ab""#, longest_palindrome_subseq("ab"), 1);
}

#[test]
fn all_same() {
    check!(r#"s = "aaaa""#, longest_palindrome_subseq("aaaa"), 4);
}

#[test]
fn not_rearranged() {
    check!(r#"s = "abab""#, longest_palindrome_subseq("abab"), 3);
}

#[test]
fn inner_skip() {
    check!(r#"s = "agbdba""#, longest_palindrome_subseq("agbdba"), 5);
}

#[test]
fn word() {
    check!(r#"s = "character""#, longest_palindrome_subseq("character"), 5);
}

#[test]
fn long_run() {
    check!(r#"s = "aaa…a" (2000)"#, longest_palindrome_subseq(&"a".repeat(2000)), 2000);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1226);
    for _ in 0..300 {
        let n = rng.below(12);
        let s = rng.string(n, "abc");
        let b = s.as_bytes();
        let mut want = 0;
        for mask in 0u32..(1 << n) {
            let picked: Vec<u8> = (0..n).filter(|&i| mask >> i & 1 == 1).map(|i| b[i]).collect();
            if picked.iter().eq(picked.iter().rev()) {
                want = want.max(picked.len());
            }
        }
        check!(format!("s = {s:?}"), longest_palindrome_subseq(&s), want);
    }
}

#[test]
fn scale_2000() {
    let s: String = (0..2000u64).map(|i| (b'a' + (i * 7919 % 26) as u8) as char).collect();
    check!("s[i] = 'a' + (7919·i) % 26, 2000 characters", longest_palindrome_subseq(&s), 153);
}
