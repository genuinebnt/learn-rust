use solution::*;

#[test]
fn both_empty() {
    check!(r#"s = "", t = """#, num_distinct("", ""), 1);
}

#[test]
fn single() {
    check!(r#"s = "a", t = "a""#, num_distinct("a", "a"), 1);
}

#[test]
fn t_longer() {
    check!(r#"s = "ab", t = "abc""#, num_distinct("ab", "abc"), 0);
}

#[test]
fn one_letter_three_times() {
    check!(r#"s = "aaa", t = "a""#, num_distinct("aaa", "a"), 3);
}

#[test]
fn overlapping() {
    check!(r#"s = "abab", t = "ab""#, num_distinct("abab", "ab"), 3);
}

#[test]
fn order_matters() {
    check!(r#"s = "ba", t = "ab""#, num_distinct("ba", "ab"), 0);
}

#[test]
fn near_u64_max() {
    check!(r#"s = 64 a's, t = 32 a's"#, num_distinct(&"a".repeat(64), &"a".repeat(32)), 1_832_624_140_942_590_534);
}

#[test]
fn dead_counts_overflow() {
    check!(r#"s = 200 a's, t = 100 a's then c"#, num_distinct(&"a".repeat(200), &format!("{}c", "a".repeat(100))), 0);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1229);
    for _ in 0..300 {
        let (ls, lt) = (rng.below(12), rng.below(4));
        let s = rng.string(ls, "ab");
        let t = rng.string(lt, "ab");
        let sb = s.as_bytes();
        let mut want = 0u64;
        for mask in 0u32..(1 << ls) {
            let picked: Vec<u8> = (0..ls).filter(|&i| mask >> i & 1 == 1).map(|i| sb[i]).collect();
            want += (picked == t.as_bytes()) as u64;
        }
        check!(format!("s = {s:?}, t = {t:?}"), num_distinct(&s, &t), want);
    }
}

#[test]
fn scale_10k() {
    let s: String = (0..10_000u64).map(|i| (b'a' + (i * 7919 % 26) as u8) as char).collect();
    let t: String = (0..9u64).map(|i| (b'a' + ((i * 104_729 + 5) % 26) as u8) as char).collect();
    check!(format!("s[i] = 'a' + (7919·i) % 26 (10000 letters), t = {t:?}"), num_distinct(&s, &t), 536_473_971_710_831_440);
}
