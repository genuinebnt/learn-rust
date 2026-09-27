use solution::*;

/// "ok" if `got` is a rearrangement of `s` with no two equal neighbours, otherwise what's wrong.
fn verdict(s: &str, got: Option<String>) -> String {
    let Some(t) = got else {
        return "None".to_string();
    };
    let (mut a, mut b): (Vec<char>, Vec<char>) = (s.chars().collect(), t.chars().collect());
    if let Some(i) = b.windows(2).position(|w| w[0] == w[1]) {
        return format!("{t:?} has {:?} twice in a row at char {i}", b[i]);
    }
    a.sort_unstable();
    b.sort_unstable();
    if a != b {
        return format!("{t:?} is not a rearrangement of the input");
    }
    "ok".to_string()
}

#[test]
fn pair_of_same() {
    check!(r#"s = "aa""#, reorganize("aa"), None);
}

#[test]
fn pair_of_different() {
    check!(r#"s = "ab" (any valid answer)"#, verdict("ab", reorganize("ab")), "ok");
}

#[test]
fn three_kinds() {
    check!(r#"s = "aaabbbccc" (any valid answer)"#, verdict("aaabbbccc", reorganize("aaabbbccc")), "ok");
}

#[test]
fn crabs_and_spaces() {
    check!(r#"s = "🦀🦀 🦀 x" (any valid answer)"#, verdict("🦀🦀 🦀 x", reorganize("🦀🦀 🦀 x")), "ok");
}

#[test]
fn case_matters() {
    check!(r#"s = "aAaA" (any valid answer)"#, verdict("aAaA", reorganize("aAaA")), "ok");
}

#[test]
fn half_plus_one() {
    check!(r#"s = "aaaabbb" (4 of 7)"#, reorganize("aaaabbb"), Some("abababa".to_string()));
}

#[test]
fn too_many_by_one() {
    check!(r#"s = "aaaabb" (4 of 6)"#, reorganize("aaaabb"), None);
}

#[test]
fn unicode_impossible() {
    check!(r#"s = "日日日本""#, reorganize("日日日本"), None);
}

#[test]
fn mostly_one() {
    check!(r#"s = "vvvvvabcd" (any valid answer)"#, verdict("vvvvvabcd", reorganize("vvvvvabcd")), "ok");
}

#[test]
fn random_vs_brute_force() {
    // Is there any arrangement? Backtracking over counts is the brute force.
    fn possible(counts: &mut [usize], last: Option<usize>, left: usize) -> bool {
        if left == 0 {
            return true;
        }
        for i in 0..counts.len() {
            if counts[i] > 0 && Some(i) != last {
                counts[i] -= 1;
                let ok = possible(counts, Some(i), left - 1);
                counts[i] += 1;
                if ok {
                    return true;
                }
            }
        }
        false
    }
    let mut rng = anneal_prelude::Rng::new(710);
    for _ in 0..300 {
        let len = rng.below(9);
        let s = rng.string(len, "abé");
        let mut counts: Vec<usize> = ['a', 'b', 'é'].iter().map(|&c| s.chars().filter(|&x| x == c).count()).collect();
        let got = reorganize(&s);
        let want = if possible(&mut counts, None, len) { "ok" } else { "None" };
        check!(format!("s = {s:?}"), verdict(&s, got), want);
    }
}

#[test]
fn scale_50k_kinds() {
    // 20000 kinds five times each, 30000 more kinds once or twice, and 30000 copies of 'x'.
    let mut s: String = (0..100_000).map(|i| char::from_u32(0x4E00 + i % 20_000).unwrap()).collect();
    s.extend((0..50_000).map(|i| char::from_u32(0x1_0000 + i % 30_000).unwrap()));
    s.push_str(&"x".repeat(30_000));
    check!("s = 180000 chars of 50001 kinds, 30000 of them 'x'", verdict(&s, reorganize(&s)), "ok");
}

#[test]
fn scale_two_kinds_exactly_half() {
    let s = "ab".repeat(50_000) + "a";
    let want = "ab".repeat(50_000) + "a";
    check!("s = \"ab\" × 50000 + \"a\" (only one answer)", reorganize(&s) == Some(want), true);
}
