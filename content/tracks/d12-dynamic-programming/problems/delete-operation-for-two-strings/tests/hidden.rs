use solution::*;

#[test]
fn both_empty() {
    check!(r#"a = "", b = """#, min_distance("", ""), 0);
}

#[test]
fn second_empty() {
    check!(r#"a = "abc", b = """#, min_distance("abc", ""), 3);
}

#[test]
fn nothing_shared() {
    check!(r#"a = "abc", b = "def""#, min_distance("abc", "def"), 6);
}

#[test]
fn reversed() {
    check!(r#"a = "abc", b = "cba""#, min_distance("abc", "cba"), 4);
}

#[test]
fn swap() {
    check!(r#"a = "ab", b = "ba""#, min_distance("ab", "ba"), 2);
}

#[test]
fn repeats() {
    check!(r#"a = "aaaa", b = "aa""#, min_distance("aaaa", "aa"), 2);
}

#[test]
fn mixed() {
    check!(r#"a = "ezupkr", b = "ubmrapg""#, min_distance("ezupkr", "ubmrapg"), 9);
}

#[test]
fn one_letter_differs() {
    check!(r#"a = "abcxdef", b = "abcydef""#, min_distance("abcxdef", "abcydef"), 2);
}

#[test]
fn random_vs_brute_force() {
    fn dist(a: &[u8], b: &[u8]) -> usize {
        match (a, b) {
            ([], _) => b.len(),
            (_, []) => a.len(),
            ([x, ra @ ..], [y, rb @ ..]) if x == y => dist(ra, rb),
            ([_, ra @ ..], [_, rb @ ..]) => 1 + dist(ra, b).min(dist(a, rb)),
        }
    }
    let mut rng = anneal_prelude::Rng::new(1225);
    for _ in 0..300 {
        let (la, lb) = (rng.below(8), rng.below(8));
        let a = rng.string(la, "abc");
        let b = rng.string(lb, "abc");
        check!(format!("a = {a:?}, b = {b:?}"), min_distance(&a, &b), dist(a.as_bytes(), b.as_bytes()));
    }
}

#[test]
fn scale_2000() {
    let a: String = (0..2000u64).map(|i| (b'a' + (i * 7919 % 26) as u8) as char).collect();
    let b: String = (0..2000u64).map(|i| (b'a' + ((i * 104_729 + 13) % 26) as u8) as char).collect();
    check!("a[i] = 'a' + (7919·i) % 26, b[i] = 'a' + (104729·i + 13) % 26, 2000 each", min_distance(&a, &b), 2770);
}
